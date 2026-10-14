# Identified issues and fixes

Line numbers refer to the unchanged starter in `reports/before/gym_system.py`.
Bandit supplies the High rating below. Other priorities are our assessment;
Pylint and Flake8 do not assign Bandit's security severity levels.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Shell injection (Bandit B605, High) | Security | 35-36 | The prefix is concatenated into an `os.system` command. Shell metacharacters could execute commands; `rm` also fails on Windows. | Iterate over the current directory with pathlib and unlink only matching JSON files. Reject empty/path prefixes, skip directories and symlinks, and treat the prefix literally. |
| Mutable default (Pylint W0102, Medium priority) | Bug | 8, 15 | The default attendance list is shared between calls and retains unrelated booking entries. | Default to `None`; append only to an explicitly supplied log. |
| Bare exception (Pylint W0702, Flake8 E722, Medium priority) | Reliability | 19-22 | Cancellation hides every exception, including unexpected programming errors. | Catch only `KeyError` and `ValueError` and return a success indicator. |
| Unclosed export file (Pylint R1732, Medium priority) | Resource handling | 31-33 | The file is never explicitly closed, risking incomplete output and retained file handles. | Use a context manager with UTF-8 encoding (also fixes W1514). |
| Missing documentation (Pylint C0114/C0116, Low priority) | Maintainability | 1, 8, 18, 24, 27, 31, 35, 38, 42 | The module and public functions do not describe their contracts. | Add module and function docstrings. |
| Naming and iteration (Pylint C0103/C0206/C0209, Low priority) | Style | 15, 27, 39-40 | Camel-case function name, legacy string formatting, and repeated dictionary lookups. | Rename `addMembers` to `add_members`, use f-strings and `.items()`, and update callers. |
| Function spacing (Flake8 E302/E305, Low priority) | Formatting | 8, 18, 24, 27, 31, 35, 38, 42, 58 | Top-level definitions and trailing code lack two blank lines. | Add the required blank lines and normalize line endings. |

## Additional behavior bugs found by running and reviewing the program

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Capacity off by one | Bug | 11 | `>` allows a fourth member in a three-seat class. | Reject when the roster length is `>=` capacity. |
| Unknown classes accepted | Validation | 9-14 | An unconfigured class such as Pilates accepts its first member. | Reject classes missing from the capacity dictionary before creating a roster. |
| Invalid capacity | Validation | 24-25, 47 | Negative seats are accepted. | Require a non-negative integer, reject booleans, and prevent shrinking below existing bookings. |
| Invalid walk-in input | Validation | 52-53 | `abc` crashes the program and negative counts are silently ignored. | Prompt again until a non-negative whole number is supplied. |
| Duplicate bookings and guest IDs | Bug | 14, 27-29 | Members can book repeatedly; successive guest batches reuse IDs. | Reject duplicate members and choose unused guest IDs. |
| Execution during import | Maintainability | 58 | Importing the file prompts for input and performs export/deletion. | Add the `if __name__ == "__main__"` guard. |

## Verification

Analysis target: `gym_system.py`, using default tool settings, without disabled
rules or `nosec` suppressions. The archived starter is intentionally unchanged.

| Tool | Before | After |
|---|---|---|
| Pylint 4.1.3 | 6.60/10; 16 messages | 10.00/10; no messages |
| Flake8 7.4.1 | 10 findings | No findings; exit 0 |
| Bandit 1.9.4 | One High/High-confidence B605 finding | No findings; exit 0 |
| unittest | No starter tests | 9 passing tests, including 4 CLI input scenarios |

Reports are in `reports/before/` and `reports/after/`; root-level report files
contain the final results. An empty Flake8 report means no findings. Baseline
runs used temporary directories to isolate the original shell deletion call.
