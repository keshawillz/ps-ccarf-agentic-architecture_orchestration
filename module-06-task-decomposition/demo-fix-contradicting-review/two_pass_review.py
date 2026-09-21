"""Demo: Fix a code review that contradicts itself.

The failure: one pass over a whole pull request flags a pattern in one file
and approves the same pattern in another. The exam calls the cause attention
dilution.

The fix is prompt chaining. This file is a chain of three model calls with a
code check between each one:

    per-file review  ->  gate  ->  integration  ->  reconcile  ->  gate

Every step is one plain API call. Text in, text out, no tools. Python reads
the files, Python decides the order, and Python hands each step's output to
the next. The gates are ordinary if-statements that stop the chain when a
step comes back wrong. That is what makes this a workflow and not an agent.

Run it:
    python two_pass_review.py
"""

import glob
import sys

import anthropic

MODEL = "claude-sonnet-5"
TARGET = "../review-target"

REVIEW_CRITERIA = """Report only:
- a handler that does not validate a required field when a sibling handler does
- a state change that skips the audit log when comparable changes record one
- an exception raised where comparable code returns an error value
Skip style, naming, and anything cosmetic. For each finding give FILE, LINE,
ISSUE, FIX. If there is nothing to report, say NO FINDINGS."""

client = anthropic.Anthropic()


def ask(prompt):
    """One plain API call. Text in, text out. No tools."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in response.content:
        if block.type == "text":
            text = text + block.text
    return text


def read_file(path):
    """Python does the reading, so the model never needs a tool."""
    with open(path) as handle:
        return handle.read()


# --- Step 1 -----------------------------------------------------------------

def review_each_file(files):
    """One focused call per file. Each call sees a single file and nothing else."""
    findings = ""
    for path in files:
        print(f"  reviewing {path}")
        prompt = (
            f"Review only this file: {path}\n\n"
            f"```python\n{read_file(path)}\n```\n\n"
            f"{REVIEW_CRITERIA}\n"
            "Judge it on its own. You have not seen any other file."
        )
        findings = findings + f"\n\n## {path}\n" + ask(prompt)
    return findings


def gate_every_file_reviewed(files, findings):
    """Code check: every file must have a section before we go on."""
    for path in files:
        if f"## {path}" not in findings:
            sys.exit(f"Gate failed: no review section for {path}. Stopping.")
    print("  gate passed: every file has a review section")


# --- Step 2 -----------------------------------------------------------------

def find_cross_file_issues(files, local_findings):
    """One call whose only job is comparing files to each other."""
    print("  comparing files")
    all_code = ""
    for path in files:
        all_code = all_code + f"\n\n### {path}\n```python\n{read_file(path)}\n```"
    prompt = (
        "Here are per-file review findings for a pull request:\n"
        f"{local_findings}\n\n"
        "Here is every file in the pull request:"
        f"{all_code}\n\n"
        "Report only cross-file issues: the same pattern handled differently "
        "in two files, or a change in one file that breaks an assumption in "
        "another. Give FILE, LINE, ISSUE, FIX."
    )
    return ask(prompt)


# --- Step 3 -----------------------------------------------------------------

def reconcile(local_findings, cross_file_findings):
    """One call that fixes contradictions and produces the final review.

    This is the step the demo is named for. It gets everything the earlier
    steps produced and is asked to find places where the review disagrees
    with itself: the same pattern flagged in one file and passed in another.
    """
    print("  reconciling")
    prompt = (
        "You are producing the final version of a code review.\n\n"
        "Per-file findings:\n"
        f"{local_findings}\n\n"
        "Cross-file findings:\n"
        f"{cross_file_findings}\n\n"
        "Do three things.\n"
        "1. Find every place these findings contradict each other, meaning "
        "the same pattern was flagged in one file and passed in another, or "
        "two findings give conflicting advice. Resolve each one and say how.\n"
        "2. Merge everything into one list with no duplicates.\n"
        "3. Order it: bugs that lose data or money first, consistency issues "
        "second, everything else last.\n\n"
        "End with exactly one line in this form:\n"
        "CONTRADICTIONS RESOLVED: <number>"
    )
    return ask(prompt)


def gate_reconciled(final_review):
    """Code check: the reconcile step must report its contradiction count."""
    if "CONTRADICTIONS RESOLVED:" not in final_review:
        sys.exit("Gate failed: reconcile step did not report a count. Stopping.")
    last_line = final_review.strip().splitlines()[-1]
    print(f"  gate passed: {last_line}")


# --- The chain --------------------------------------------------------------

def main():
    files = sorted(glob.glob(TARGET + "/**/*.py", recursive=True))
    print(f"Reviewing {len(files)} files as a chain of three steps.\n")

    print("Step 1: review each file on its own")
    local_findings = review_each_file(files)
    gate_every_file_reviewed(files, local_findings)

    print("\nStep 2: compare the files to each other")
    cross_file_findings = find_cross_file_issues(files, local_findings)

    print("\nStep 3: reconcile and produce the final review")
    final_review = reconcile(local_findings, cross_file_findings)
    gate_reconciled(final_review)

    print("\n" + "=" * 60)
    print(final_review)
    print("=" * 60)
    print(
        "\nThree steps, each handed the output of the one before, with a code "
        "check between them. The order was fixed before anything ran."
    )


if __name__ == "__main__":
    main()