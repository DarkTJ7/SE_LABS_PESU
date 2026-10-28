"""Lab 6: branch coverage and boundary tests for shipping_quote.py."""

import pytest

from shipping_quote import monitor_container_pressures, process_shipments


def shipment(packages, **options):
    return {"manifest_approved": True, "packages": packages, **options}


@pytest.mark.parametrize("shipments,fee", [(None, 0), ([], -1)])
def test_invalid_input(shipments, fee):
    with pytest.raises(ValueError, match="Invalid shipments list or handling fee"):
        process_shipments(shipments, fee)


def test_ground_shipment():
    assert process_shipments([shipment([{"weight_kg": 10}])], 20) == {
        "total_quote": 60.0, "status": "CLEARED"
    }


def test_air_heavy_express_shipment():
    # (20 handling + 40 kg * 12 air rate * 1.5 heavy rate) * 1.25 express.
    cargo = shipment([{"weight_kg": 40}], mode="air", express_priority=True)
    assert process_shipments([cargo], 20) == {
        "total_quote": 925.0, "status": "CLEARED"
    }


def test_unapproved_manifest_is_skipped():
    cargo = shipment([{"weight_kg": 10}], manifest_approved=False)
    assert process_shipments([cargo], 20) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_unsupported_transport_is_rejected():
    assert process_shipments([shipment([], mode="sea")], 20) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_four_invalid_packages_trigger_review():
    cargo = shipment([{"weight_kg": 0}, {"weight_kg": -1}, {}, {"weight_kg": -5}])
    assert process_shipments([cargo], 20) == {
        "total_quote": 20.0, "status": "FLAGGED_REVIEW"
    }


def test_nonfragile_hazmat_surcharge_and_continuation():
    cargo = shipment([{"weight_kg": 10, "is_hazmat": True}, {"weight_kg": 2}])
    assert process_shipments([cargo], 20) == {
        "total_quote": 78.0, "status": "CLEARED"
    }


def test_fragile_hazmat_cancels_cost_and_stops_packages():
    cargo = shipment([
        {"weight_kg": 10}, {"weight_kg": 5, "is_hazmat": True}, {"weight_kg": 20}
    ], is_fragile=True)
    assert process_shipments([cargo], 20) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_empty_pressure_logs():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_consecutive_low_pressures_detect_leak():
    assert monitor_container_pressures([[15.0, 13.0, 12.0]]) == "LEAK_DETECTED"


def test_normal_pressure_resets_streak():
    assert monitor_container_pressures([[13.0, 14.0, 13.0]]) == "STABLE"


def test_empty_shipments():
    assert process_shipments([], 20) == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_missing_manifest_defaults_to_unapproved():
    assert process_shipments([{"packages": [{"weight_kg": 10}]}], 20) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


@pytest.mark.parametrize("cargo", [shipment([]), {"manifest_approved": True}])
def test_empty_or_missing_packages_charge_handling_only(cargo):
    assert process_shipments([cargo], 20) == {
        "total_quote": 20.0, "status": "CLEARED"
    }


@pytest.mark.parametrize("mode,weight,expected", [
    ("ground", 30, 120.0), ("ground", 31, 186.0),
    ("air", 30, 360.0), ("air", 31, 558.0),
])
def test_weight_surcharge_boundary(mode, weight, expected):
    assert process_shipments([shipment([{"weight_kg": weight}], mode=mode)], 0) == {
        "total_quote": expected, "status": "CLEARED"
    }


@pytest.mark.parametrize("count,status", [(3, "NO_CARGO"), (4, "FLAGGED_REVIEW")])
def test_rejection_threshold_precedes_no_cargo(count, status):
    cargo = shipment([{"weight_kg": 0}] * count)
    assert process_shipments([cargo], 0) == {"total_quote": 0.0, "status": status}


def test_rejections_accumulate_across_shipments():
    cargo = [shipment([], mode="sea"), shipment([{}, {}, {}])]
    assert process_shipments(cargo, 10) == {
        "total_quote": 10.0, "status": "FLAGGED_REVIEW"
    }


def test_shipments_accumulate_with_individual_express_fees():
    cargo = [shipment([{"weight_kg": 10}]),
             shipment([{"weight_kg": 2}], mode="air", express_priority=True)]
    assert process_shipments(cargo, 20) == {
        "total_quote": 115.0, "status": "CLEARED"
    }


def test_invalid_weight_is_rejected_before_hazmat_and_processing_continues():
    cargo = shipment([{"weight_kg": 0, "is_hazmat": True}, {"weight_kg": 1}],
                     is_fragile=True)
    assert process_shipments([cargo], 20) == {
        "total_quote": 24.0, "status": "CLEARED"
    }


def test_hazmat_uses_flat_surcharge_even_for_heavy_package():
    cargo = shipment([{"weight_kg": 40, "is_hazmat": True}], express_priority=True)
    assert process_shipments([cargo], 20) == {
        "total_quote": 87.5, "status": "CLEARED"
    }


def test_fragile_hazmat_does_not_cancel_later_shipments():
    cargo = [shipment([{"weight_kg": 1, "is_hazmat": True}],
                      is_fragile=True, express_priority=True),
             shipment([{"weight_kg": 2}])]
    assert process_shipments(cargo, 20) == {
        "total_quote": 28.0, "status": "CLEARED"
    }


def test_quote_rounding():
    assert process_shipments([shipment([{"weight_kg": 1.234}])], 0) == {
        "total_quote": 4.94, "status": "CLEARED"
    }


@pytest.mark.parametrize("logs,expected", [
    (None, "NO_DATA"),
    ([[]], "STABLE"),
    ([[14.0]], "STABLE"),
    ([[13.99]], "STABLE"),
    ([[13.99, 13.99]], "LEAK_DETECTED"),
    ([[13.0], [13.0]], "STABLE"),
    ([[], [15.0], [13.0, 12.0]], "LEAK_DETECTED"),
    ([[13.0, 14.0, 13.0, 13.0]], "LEAK_DETECTED"),
])
def test_pressure_boundaries_and_container_independence(logs, expected):
    assert monitor_container_pressures(logs) == expected
