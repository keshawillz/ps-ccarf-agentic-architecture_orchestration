"""Checks for the codebase exploration challenge.

Two things have to be true when you're done:
  1. Both investigations ran, so the report covers tests and the refund path.
  2. Every finding is tagged with the file path it came from.

This is a keyword and pattern check, not a judge of quality. It tells you
whether the structure you were asked to build is actually there.
"""

# Files the two investigations should surface between them.
EXPECTED_PATHS = [
    "refunds.py",
    "charges.py",
    "limits.py",
    "test_refunds.py",
    "test_limits.py",
]


def check_paths(report_text):
    """Return a dict of file name -> True if the report mentions it."""
    found = {}
    for path in EXPECTED_PATHS:
        found[path] = path in report_text
    return found


def print_check(report_text, spawn_log):
    """Print both checks and say whether the run passed."""
    print("\nFile path check")
    print("-" * 34)
    found = check_paths(report_text)
    hits = 0
    for path in found:
        if found[path]:
            print(f"  TAGGED   {path}")
            hits = hits + 1
        else:
            print(f"  MISSING  {path}")
    print("-" * 34)
    print(f"{hits} of {len(found)} files traced to a path")

    print("\nParallel spawn check")
    print("-" * 34)
    if len(spawn_log) < 2:
        print(f"  Only {len(spawn_log)} subagent spawned. Expected at least 2.")
        parallel_ok = False
    else:
        gap = spawn_log[1] - spawn_log[0]
        print(f"  First two spawns {gap:.1f}s apart")
        if gap < 5.0:
            print("  Same response. They ran at the same time.")
            parallel_ok = True
        else:
            print("  Separate turns. The second waited for the first.")
            parallel_ok = False

    print("-" * 34)
    passed = (hits == len(found)) and parallel_ok
    if passed:
        print("Both checks passed.")
    else:
        print("Not there yet. See the README checklist.")
    return passed
