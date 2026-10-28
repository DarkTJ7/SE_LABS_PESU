"""Lab 6: statement coverage tests for shipping_quote.py."""

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
