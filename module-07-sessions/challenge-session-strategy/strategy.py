"""Part one of the session strategy challenge.

Write your resume prompt below. It has to name both changed files and say
what changed in each, so the resumed session re-reads only those two.

Before running this, create the session it resumes:

    cd ../demo-resume-yesterdays-investigation
    python resume_investigation.py start
"""

import asyncio
import sys

from claude_agent_sdk import ClaudeAgentOptions, query

MODEL = "claude-sonnet-5"
ID_FILE = "../demo-resume/session_id.txt"

# A session is sandboxed to its working directory, so run from the module
# folder. That puts sample-app inside the tree instead of above it.
MODULE_DIR = ".."
CHANGED_FILES = ["billing/limits.py", "billing/charges.py"]

# Replace this. Name both files in CHANGED_FILES and describe each change.
RESUME_PROMPT = """Some files changed. Please re-check your analysis."""


def check_prompt(prompt):
    """Refuse to run until the prompt names both changed files."""
    print("Prompt check")
    print("-" * 30)
    ok = True
    for path in CHANGED_FILES:
        if path in prompt:
            print(f"  NAMED    {path}")
        else:
            print(f"  MISSING  {path}")
            ok = False
    print("-" * 30)
    return ok


def read_session_id():
    """Load the session id the demo saved, or explain how to make one."""
    try:
        with open(ID_FILE) as handle:
            return handle.read().strip()
    except FileNotFoundError:
        sys.exit(
            "No session id found at " + ID_FILE + "\n"
            "Create the session first:\n"
            "    cd ../demo-resume\n"
            "    python resume_investigation.py start"
        )


async def main():
    if not check_prompt(RESUME_PROMPT):
        print(
            "Name both changed files before running. A resumed session only "
            "re-reads what you tell it changed."
        )
        sys.exit(1)

    session_id = read_session_id()
    options = ClaudeAgentOptions(
        model=MODEL,
        cwd=MODULE_DIR,
        allowed_tools=["Read", "Glob", "Grep"],
        resume=session_id,
        max_budget_usd=1.0,
    )
    async for message in query(prompt=RESUME_PROMPT, options=options):
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
