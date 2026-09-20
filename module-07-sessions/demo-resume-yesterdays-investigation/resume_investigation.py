"""Demo: Pick up yesterday's investigation.

Two ways to resume. In Claude Code, from the terminal:

    claude --resume refund-bug        # by the name you gave the session

From the SDK, you save the session id when a run finishes and pass it back as
resume. The conversation continues where it stopped, with everything the
first session read still in context.

Run it:
    python resume_investigation.py start      first session, saves the id
    python resume_investigation.py continue   resumes it with a follow-up
"""

import asyncio
import sys

from claude_agent_sdk import ClaudeAgentOptions, query

MODEL = "claude-sonnet-5"
APP = "../sample-app"
ID_FILE = "session_id.txt"

START_PROMPT = f"""Investigate the refund path in {APP}. Read billing/refunds.py and
everything it imports. Summarize how process_refund decides to refund, block,
or reject, in under 150 words. This is day one of a multi-day investigation."""

CONTINUE_PROMPT = """Day two. Based on what you read yesterday, which single
function would you test first if you could only write one test, and why?
Do not re-read the files unless you have to."""


async def run(prompt, resume_id):
    options = ClaudeAgentOptions(model=MODEL, 
                                 allowed_tools=["Read", "Glob", "Grep"],
                                 max_budget_usd=1.0)
    if resume_id is not None:
        options.resume = resume_id
    session_id = None
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, "session_id"):
            session_id = message.session_id
        if hasattr(message, "result"):
            print(message.result)
    return session_id


async def main():
    mode = "start"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    if mode == "start":
        print("=== Day one ===\n")
        session_id = await run(START_PROMPT, None)
        with open(ID_FILE, "w") as handle:
            handle.write(session_id)
        print(f"\nSaved session id to {ID_FILE}")
    else:
        with open(ID_FILE) as handle:
            session_id = handle.read().strip()
        print(f"=== Day two, resuming {session_id} ===\n")
        await run(CONTINUE_PROMPT, session_id)
        print("\nNo files were re-read. Yesterday's context was still there.")


if __name__ == "__main__":
    asyncio.run(main())
