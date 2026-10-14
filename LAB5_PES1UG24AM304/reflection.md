# Reflection

The supplied PDF contains no explicit reflection questions, although the README
refers to four. These four topics are therefore provisional reflection answers,
not quotations of missing questions. Review and personalize them before submission.

## 1. What did each static analysis tool contribute?

Pylint identified the shared mutable default, broad exception handling, missing
documentation, naming problems, and file handling problems. Flake8 identified
function spacing and the bare exception. Bandit identified shell execution with
an interpolated prefix as a high-severity security issue. Their overlap helped
confirm some problems, while their different scopes exposed different risks.

## 2. Which issues were prioritized, and how were they fixed?

Shell injection came first because a crafted prefix could run shell commands.
Replacing the shell with pathlib removed that execution path and made cleanup
work on Windows. The mutable default and unclosed export file were addressed
next, together with narrow exception handling. Formatting and documentation
were then corrected. Runtime inspection also led to fixes for overbooking,
unknown classes, invalid capacities, invalid input, and duplicate bookings.

## 3. How were the fixes verified, and what are the tools' limitations?

The original reports were preserved before editing. All three tools were rerun
on the final script: Pylint scored 10.00/10, and Flake8 and Bandit exited zero
without findings. Nine regression tests exercised booking boundaries,
cancellation, independent logs, capacity validation, guest IDs, UTF-8 JSON
exports, cleanup scope, and CLI input recovery. Static analysis did not flag
the capacity comparison or unknown-class acceptance. A clean report therefore
needs to be supported by behavior tests and code review; it is not proof that
all bugs or security risks have been eliminated.

## 4. How would static analysis fit into future development?

Run these tools before commits and in continuous integration, keep their
versions reproducible, and address security and correctness findings before
cosmetic findings. Pair the checks with tests for domain rules such as class
capacity and cancellation. Save reports when evaluating improvements, but
avoid ignoring warnings simply to increase a score. Clear function contracts
and focused exception handling also make later changes easier to review.
