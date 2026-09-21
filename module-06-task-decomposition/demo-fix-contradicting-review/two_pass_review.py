"""Demo: Fix a code review that contradicts itself.

The failure: one pass over a whole pull request flags a pattern in one file
and approves the same pattern in another, and gives some files four
paragraphs while others get one line. The exam calls the cause attention
dilution.

The fix, in the exam's own words: analyze each file individually, then run a
cross-file integration pass. Two stages. The exam calls this prompt chaining.

Every call here is one plain API call. Text in, text out, no tools. Python
reads the files, Python decides the order, and Python hands stage one's
output to stage two. That is what makes it a workflow and not an agent.

Run it:
    python two_pass_review.py
"""

import glob

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
    """One plain API call. A prompt goes in, text comes out. No tools."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
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


def stage_one(files):
    """Analyze each file individually. One call per file, one file per call."""
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


def stage_two(files, stage_one_findings):
    """Cross-file integration pass. One call that gets stage one's output."""
    print("  comparing all files together")
    all_code = ""
    for path in files:
        all_code = all_code + f"\n\n### {path}\n```python\n{read_file(path)}\n```"
    prompt = (
        "Here are per-file review findings for a pull request:\n"
        f"{stage_one_findings}\n\n"
        "Here is every file in the pull request:"
        f"{all_code}\n\n"
        "Report only cross-file issues: the same pattern handled differently "
        "in two files, or a change in one file that breaks an assumption in "
        "another. Give FILE, LINE, ISSUE, FIX."
    )
    return ask(prompt)


def main():
    files = sorted(glob.glob(TARGET + "/**/*.py", recursive=True))
    print(f"Reviewing {len(files)} files in two stages.\n")

    print("Stage 1: analyze each file individually")
    stage_one_findings = stage_one(files)
    print("\n--- stage 1 findings ---")
    print(stage_one_findings)

    print("\nStage 2: cross-file integration pass")
    stage_two_findings = stage_two(files, stage_one_findings)
    print("\n--- stage 2 findings ---")
    print(stage_two_findings)

    print(
        "\nStage 1 gave every file the same attention. Stage 2 is the only "
        "call that was asked to compare files, and it got stage 1's findings "
        "as its input. That handoff is the chain."
    )


if __name__ == "__main__":
    main()