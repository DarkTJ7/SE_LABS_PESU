"""Regression tests for booking behavior, exports, and input handling."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import gym_system as gym


class BookingTests(unittest.TestCase):
    """Verify ledger invariants and safe file operations."""

    def setUp(self):
        gym.class_capacity.clear()
        gym.class_capacity.update({"Yoga": 3, "HIIT": 2, "Spin": 4})
        gym.rosters.clear()

    def test_capacity_boundary_and_duplicate(self):
        for member in ("M1", "M2", "M3"):
            self.assertTrue(gym.book_class(member, "Yoga"))
        self.assertFalse(gym.book_class("M4", "Yoga"))
        self.assertFalse(gym.book_class("M1", "Yoga"))
        self.assertEqual(gym.rosters["Yoga"], ["M1", "M2", "M3"])

    def test_unknown_and_zero_capacity(self):
        self.assertFalse(gym.book_class("M1", "Pilates"))
        self.assertNotIn("Pilates", gym.rosters)
        gym.set_capacity("Spin", 0)
        self.assertFalse(gym.book_class("M1", "Spin"))

    def test_explicit_attendance_logs_are_independent(self):
        first, second = [], []
        gym.book_class("M1", "Yoga", first)
        gym.book_class("M2", "Yoga", second)
        self.assertEqual(first, ["M1 -> Yoga"])
        self.assertEqual(second, ["M2 -> Yoga"])

    def test_cancellation(self):
        self.assertFalse(gym.cancel_booking("M1", "Missing"))
        gym.book_class("M1", "Yoga")
        self.assertFalse(gym.cancel_booking("M2", "Yoga"))
        self.assertTrue(gym.cancel_booking("M1", "Yoga"))
        self.assertEqual(gym.rosters["Yoga"], [])

    def test_capacity_validation(self):
        for value in (-1, 1.5, True, "3"):
            with self.assertRaises(ValueError):
                gym.set_capacity("Yoga", value)
        gym.book_class("M1", "Yoga")
        with self.assertRaises(ValueError):
            gym.set_capacity("Yoga", 0)
        self.assertEqual(gym.class_capacity["Yoga"], 3)

    def test_guest_ids_and_validation(self):
        gym.add_members("Spin", 2)
        gym.add_members("Spin", 3)
        self.assertEqual(gym.rosters["Spin"],
                         ["GUEST-0", "GUEST-1", "GUEST-2", "GUEST-3"])
        for count in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                gym.add_members("Spin", count)

    def test_json_export(self):
        gym.book_class("M\u00e9", "Yoga")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "schedule.json"
            gym.export_roster(path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")),
                             {"Yoga": ["M\u00e9"]})
            path.unlink()  # Also confirms that the file was closed on Windows.

    def test_cleanup_scope_and_literal_prefix(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            os.chdir(folder)
            try:
                for name in ("old_a.json", "keep.json", "old_a.txt"):
                    Path(name).write_text("test", encoding="utf-8")
                Path("old_directory.json").mkdir()
                gym.clear_old_exports()
                self.assertFalse(Path("old_a.json").exists())
                for name in ("keep.json", "old_a.txt", "old_directory.json"):
                    self.assertTrue(Path(name).exists())
                gym.clear_old_exports("old_;echo injected")
                for prefix in ("", "../", "..\\"):
                    with self.assertRaises(ValueError):
                        gym.clear_old_exports(prefix)
            finally:
                os.chdir(previous)

    def test_cli_inputs(self):
        script = str(Path(gym.__file__).resolve())
        for value in ("\n", "3\n", "abc\n-1\n2\n", "0\n"):
            with tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    [sys.executable, script], input=value, cwd=folder,
                    capture_output=True, text=True, check=False, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads((Path(folder) / "gym_schedule.json")
                                  .read_text(encoding="utf-8"))
                self.assertEqual(len(data["Yoga"]), 3)
                self.assertLessEqual(len(data["HIIT"]), 2)
                self.assertEqual(len(data["Spin"]), 3)
                self.assertNotIn("Pilates", data)
                if "abc" in value:
                    self.assertEqual(result.stdout.count(
                        "Please enter a non-negative whole number."), 2)


if __name__ == "__main__":
    with contextlib.redirect_stdout(io.StringIO()):
        unittest.main()
