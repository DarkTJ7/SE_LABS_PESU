"""The same tests run against the original and fixed processor modules."""

import json
import math
import string

import pytest
from hypothesis import given, settings, strategies as st
from processor import (calculate_dimensional_weight, format_tracking_label,
                       parse_package_manifest)


@settings(max_examples=300, deadline=None)
@given(st.text() | st.none())
def test_calculate_dimensional_weight_no_crash(s):
    try:
        result = calculate_dimensional_weight(s)
    except Exception as error:
        pytest.fail("dimensions crashed for {!r}: {!r}".format(s, error))
    assert result is None or (isinstance(result, float)
                              and math.isfinite(result) and result >= 0)


@settings(max_examples=300, deadline=None)
@given(st.text() | st.none())
def test_format_tracking_label_safe(s):
    try:
        result = format_tracking_label(s)
    except Exception as error:
        pytest.fail("tracking crashed for {!r}: {!r}".format(s, error))
    if result is not None:
        assert len(result) == 8
        assert result[0] in string.ascii_uppercase and result[1] == "-"
        assert all(char in string.digits for char in result[2:])


@settings(max_examples=300, deadline=None)
@given(st.text() | st.none())
def test_parse_package_manifest_safe(s):
    try:
        result = parse_package_manifest(s)
    except Exception as error:
        pytest.fail("manifest crashed for {!r}: {!r}".format(s, error))
    assert result is None or (isinstance(result, float)
                              and math.isfinite(result) and result >= 0)


@given(length=st.integers(1, 10000), width=st.integers(1, 10000),
       height=st.integers(1, 10000))
def test_valid_dimensions(length, width, height):
    text = "{}x{}x{}".format(length, width, height)
    assert calculate_dimensional_weight(text) == round(length * width * height / 5000.0, 2)


@given(prefix=st.sampled_from(list(string.ascii_letters)),
       number=st.integers(0, 999999))
def test_valid_tracking_codes(prefix, number):
    assert format_tracking_label(prefix + str(number)) == "{}-{:06d}".format(prefix.upper(), number)


@given(weight=st.floats(min_value=0, max_value=1e100,
                        allow_nan=False, allow_infinity=False))
def test_valid_manifest_weights(weight):
    assert parse_package_manifest(json.dumps({"weight": weight})) == weight
    assert parse_package_manifest(json.dumps({"weight": str(weight)})) == weight


@given(st.sampled_from(["", "1x2", "1x2x3x4", "0x2x3", "-1x2x3",
                       "nanx2x3", "infx2x3", "1e308x1e308x1e308",
                       "axbxc", "x" * 4097]))
def test_invalid_dimensions_return_none(value):
    assert calculate_dimensional_weight(value) is None


@given(st.sampled_from(["", "E", "1123", "E-123", "E+123", "E1234567",
                       "E1.5", "E12 3", "\u00e9123", "E\u0661\u0662", "E" * 4097]))
def test_invalid_tracking_returns_none(value):
    assert format_tracking_label(value) is None


@given(st.sampled_from(["", "{", "{}", "[]", "null", "42", '"text"',
                       '{"weight":null}', '{"weight":true}',
                       '{"weight":[]}', '{"weight":{}}', '{"weight":-1}',
                       '{"weight":"bad"}', '{"weight":NaN}',
                       '{"weight":Infinity}', '{"weight":1e999}',
                       "[" * 1500 + "0" + "]" * 1500]))
def test_invalid_manifest_returns_none(value):
    assert parse_package_manifest(value) is None


@given(st.one_of(st.none(), st.booleans(), st.integers(),
                 st.floats(), st.lists(st.integers()),
                 st.dictionaries(st.text(max_size=10), st.integers()), st.binary()))
def test_nonstring_inputs_are_rejected(value):
    assert calculate_dimensional_weight(value) is None
    assert format_tracking_label(value) is None
    assert parse_package_manifest(value) is None


def test_examples_whitespace_and_zero_weight():
    assert calculate_dimensional_weight("20x30x10") == 1.2
    assert calculate_dimensional_weight(" 20 X 30 X 10 ") == 1.2
    assert format_tracking_label(" e123 ") == "E-000123"
    assert parse_package_manifest('{"weight":12.5}') == 12.5
    assert parse_package_manifest('{"weight":0}') == 0.0
    assert parse_package_manifest('{"weight":"0"}') == 0.0
