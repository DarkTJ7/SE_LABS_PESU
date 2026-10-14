import json
from pathlib import Path

# Global state
class_capacity = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}

def book_class(member_id, class_name, attendance_log=[]):
    if class_name not in rosters:
        rosters[class_name] = []
    if len(rosters[class_name]) > class_capacity.get(class_name, 0):
        print("Class full:", class_name)
        return False
    rosters[class_name].append(member_id)
    attendance_log.append("%s -> %s" % (member_id, class_name))
    return True

def cancel_booking(member_id, class_name):
    try:
        rosters[class_name].remove(member_id)
    except:
        print("Nothing to cancel")

def set_capacity(class_name, seats):
    class_capacity[class_name] = seats

def addMembers(class_name, count):
    for i in range(count):
        book_class("GUEST-" + str(i), class_name)

def export_roster(file="gym_schedule.json"):
    f = open(file, "w")
    json.dump(rosters, f)

def clear_old_exports(prefix="old_"):
    if not prefix or "/" in prefix or "\\" in prefix:
        raise ValueError("Prefix must be a non-empty filename prefix")
    for path in Path.cwd().iterdir():
        if path.name.startswith(prefix) and path.suffix == ".json":
            if path.is_file() and not path.is_symlink():
                path.unlink()

def show_rosters():
    for c in rosters:
        print(c, ":", ", ".join(str(m) for m in rosters[c]))

def main():
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class(55, "HIIT")
    book_class("M5", "Pilates")
    set_capacity("Spin", -2)
    addMembers("Spin", 3)
    cancel_booking("M9", "Boxing")
    n = input("How many walk-in guests for HIIT? (Enter for 1): ") or "1"
    addMembers("HIIT", int(n))
    clear_old_exports()
    export_roster()
    show_rosters()

main()
