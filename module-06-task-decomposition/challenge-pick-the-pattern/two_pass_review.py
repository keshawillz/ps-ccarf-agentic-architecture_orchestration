"""Challenge part two: run the review and study both stages.

Same script from the demo. Run it, then answer two questions:

  What did stage 2 find that stage 1 had no way of finding?
  What did stage 1 catch that stage 2 was not looking for?

Write down both, and why in each case.

Run it:
    python two_pass_review.py
"""

import asyncio
import glob

from claude_agent_sdk import ClaudeAgentOptions, query

MODEL = "claude-sonnet-5"
TARGET = "../review-target"

REVIEW_CRITERIA = """Report only:
- a handler that does not validate a required field when a sibling handler does
- a state change that skips the audit log when comparable changes record one
- an exception raised where comparable code returns an error value
Skip style, naming, and anything cosmetic. For each finding give FILE, LINE,
ISSUE, FIX."""


async def ask(prompt, allowed_tools):
    """Send one prompt and return the text that comes back."""
    options = ClaudeAgentOptions(model=MODEL, allowed_tools=allowed_tools,
                                 max_budget_usd=1.5)
    result = ""
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, "result"):
            result = message.result
    return result


async def local_passes(files):
    """One focused pass per file. Each one sees a single file and nothing else."""
    findings = ""
    for path in files:
        print(f"  local pass: {path}")
        prompt = (f"Review only this file: {path}. Read it and nothing else.\n\n"
                  f"{REVIEW_CRITERIA}\n"
                  "Judge it on its own. Do not compare it to other files.")
        findings = findings + f"\n\n## {path}\n" + await ask(prompt, ["Read"])
    return findings


async def integration_pass(local_findings):
    """One pass whose only job is comparing files to each other."""
    print("  integration pass: cross-file consistency")
    prompt = (f"Here are per-file review findings for a pull request:\n"
              f"{local_findings}\n\n"
              f"Now read every .py file under {TARGET} together and report only "
              "cross-file issues: the same pattern handled differently in two "
              "files, or a change in one file that breaks an assumption in "
              "another. Give FILE, LINE, ISSUE, FIX.")
    return await ask(prompt, ["Read", "Glob", "Grep"])


async def main():
    files = sorted(glob.glob(TARGET + "/**/*.py", recursive=True))
    print(f"Reviewing {len(files)} files in two stages.\n")

    print("Stage 1: one focused pass per file")
    local_findings = await local_passes(files)
    print("\n--- local findings ---")
    print(local_findings)

    print("\nStage 2: one pass across all files")
    cross_file = await integration_pass(local_findings)
    print("\n--- cross-file findings ---")
    print(cross_file)

    print(
        "\nStage 1 gave every file the same depth. Stage 2 is the only step "
        "that was asked to compare files, so the comparison happened by "
        "design rather than by luck."
    )


if __name__ == "__main__":
    asyncio.run(main())
