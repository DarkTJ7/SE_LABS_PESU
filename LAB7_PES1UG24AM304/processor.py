"""Shipping quotation helpers. Invalid input returns None; valid zero is preserved.

Policy chosen for this lab (the starter does not define an invalid-input return):
* Dimensions: three positive finite numbers separated by x/X, in centimetres.
* Tracking code: one ASCII letter and one to six ASCII digits (000000-999999).
* Manifest: a JSON object with a nonnegative finite numeric/numeric-string weight.
* Outer whitespace is accepted. Text is limited to 4096 characters for resources.
"""

import json
import math
import re
from typing import Optional

MAX_INPUT_LENGTH = 4096


def _clean_text(value) -> Optional[str]:
    if not isinstance(value, str) or len(value) > MAX_INPUT_LENGTH:
        return None
    return value.strip()


def calculate_dimensional_weight(dimensions_str) -> Optional[float]:
    """Return rounded dimensional kg, or None for invalid/unrepresentable input."""
    text = _clean_text(dimensions_str)
    if not text:
        return None
    parts = re.split("[xX]", text)
    if len(parts) != 3:
        return None
    try:
        length, width, height = (float(part) for part in parts)
        if not all(math.isfinite(value) and value > 0
                   for value in (length, width, height)):
            return None
        weight = (length * width * height) / 5000.0
        if not math.isfinite(weight):
            return None
        return round(weight, 2)
    except (ValueError, TypeError, OverflowError):
        return None


def format_tracking_label(raw_code) -> Optional[str]:
    """Return LETTER-000000, or None when the raw code violates its format."""
    text = _clean_text(raw_code)
    if not text:
        return None
    match = re.fullmatch(r"([A-Za-z])([0-9]{1,6})", text)
    if match is None:
        return None
    prefix, digits = match.groups()
    return "{}-{:06d}".format(prefix.upper(), int(digits))


def parse_package_manifest(json_payload) -> Optional[float]:
    """Read a finite, nonnegative weight from a JSON object; otherwise None."""
    text = _clean_text(json_payload)
    if not text:
        return None
    try:
        data = json.loads(text)
        if not isinstance(data, dict) or "weight" not in data:
            return None
        value = data["weight"]
        # bool is an int subclass, but is not a package weight.
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            return None
        weight = float(value)
        return weight if math.isfinite(weight) and weight >= 0 else None
    except (ValueError, TypeError, OverflowError, RecursionError):
        return None


def main():
    tasks = (
        ("calculate_dimensional_weight",
         "Enter dimensions LxWxH in cm (e.g. 20x30x10): ",
         calculate_dimensional_weight, "Dimensional Weight (kg)",
         "Invalid dimensions: enter three positive finite numbers, e.g. 20x30x10."),
        ("format_tracking_label", "Enter raw code (e.g. E123): ",
         format_tracking_label, "Formatted Label",
         "Invalid tracking code: enter one letter and 1-6 digits, e.g. E123."),
        ("parse_package_manifest",
         'Enter manifest JSON (e.g. {"weight": 12.5}): ',
         parse_package_manifest, "Manifest Weight",
         "Invalid manifest: supply a JSON object with a finite nonnegative weight."),
    )
    for index, (name, prompt, function, label, error) in enumerate(tasks):
        if index:
            print()
        print("==== Running {} ====".format(name))
        try:
            value = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        result = function(value)
        print(error if result is None else "{}: {}".format(label, result))


if __name__ == "__main__":
    main()
