"""Book gym classes, manage capacity, and export member rosters."""

import json
from pathlib import Path

class_capacity = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}


def book_class(member_id, class_name, attendance_log=None):
    """Book a unique member into a known class with an available seat."""
    if class_name not in class_capacity:
        print("Unknown class:", class_name)
        return False
    roster = rosters.setdefault(class_name, [])
    if member_id in roster:
        print("Already booked:", member_id, class_name)
        return False
    if len(roster) >= class_capacity[class_name]:
        print("Class full:", class_name)
        return False
    roster.append(member_id)
    if attendance_log is not None:
        attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Cancel a booking, returning whether a member was removed."""
    try:
        rosters[class_name].remove(member_id)
    except (KeyError, ValueError):
        print("Nothing to cancel")
        return False
    return True


def set_capacity(class_name, seats):
    """Set a non-negative integer capacity without displacing bookings."""
    if isinstance(seats, bool) or not isinstance(seats, int) or seats < 0:
        raise ValueError("Capacity must be a non-negative integer")
    if seats < len(rosters.get(class_name, [])):
        raise ValueError("Capacity cannot be smaller than the current roster")
    class_capacity[class_name] = seats


def add_members(class_name, count):
    """Attempt to book count new guests, using distinct guest IDs."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Guest count must be a non-negative integer")
    guest_number = 0
    for _ in range(count):
        while f"GUEST-{guest_number}" in rosters.get(class_name, []):
            guest_number += 1
        if not book_class(f"GUEST-{guest_number}", class_name):
            break
        guest_number += 1


def export_roster(file="gym_schedule.json"):
    """Write the current rosters to a UTF-8 JSON file."""
    with open(file, "w", encoding="utf-8") as roster_file:
        json.dump(rosters, roster_file, indent=2)


def clear_old_exports(prefix="old_"):
    """Delete matching JSON files in the current directory without a shell."""
    if not prefix or "/" in prefix or "\\" in prefix:
        raise ValueError("Prefix must be a non-empty filename prefix")
    for path in Path.cwd().iterdir():
        if path.name.startswith(prefix) and path.suffix == ".json":
            if path.is_file() and not path.is_symlink():
                path.unlink()


def show_rosters():
    """Display the members booked into each class."""
    for class_name, members in rosters.items():
        print(class_name, ":", ", ".join(str(member) for member in members))


def main():
    """Run the booking demonstration and accept a walk-in guest count."""
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class(55, "HIIT")
    book_class("M5", "Pilates")
    try:
        set_capacity("Spin", -2)
    except ValueError as error:
        print(error)
    add_members("Spin", 3)
    cancel_booking("M9", "Boxing")
    while True:
        value = input("How many walk-in guests for HIIT? (Enter for 1): ")
        try:
            count = int(value or "1")
            if count < 0:
                raise ValueError("Negative count")
        except ValueError:
            print("Please enter a non-negative whole number.")
            continue
        break
    add_members("HIIT", count)
    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()
