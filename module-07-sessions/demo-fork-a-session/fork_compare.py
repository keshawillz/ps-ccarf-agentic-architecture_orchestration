"""Demo: Fork a session to compare two approaches.

Module 3 forked with options.fork_session=True on a resumed query. This demo
uses the SDK's standalone fork_session() function, which copies a finished
session into a new one you can then resume independently. Same idea, one
level lower: you get a new session id back and decide what to do with it.

Both forks inherit the baseline analysis. Neither can see the other.

Run it:
    python fork_compare.py
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, fork_session, query

MODEL = "claude-sonnet-5"

# Run from the module folder so sample-app is inside the working directory.
# A session is sandboxed to its cwd, so "../sample-app" is unreadable from here.
MODULE_DIR = ".."
APP = "sample-app"

BASELINE = f"""Read {APP}/billing/refunds.py and its imports. Note every place
partial_refund and process_refund duplicate logic. Under 120 words."""

APPROACH_A = """Propose refactoring the duplicated logic into one shared helper
that both functions call. Under 100 words."""

APPROACH_B = """Propose refactoring by making partial_refund call process_refund
with a computed amount. Under 100 words."""


async def run(prompt, resume_id):
    options = ClaudeAgentOptions(model=MODEL, 
                                 allowed_tools=["Read", "Glob", "Grep"],
                                 cwd=MODULE_DIR,
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
    print("=== Baseline: one expensive read ===\n")
    baseline_id = await run(BASELINE, None)

    fork_a = fork_session(baseline_id, title="approach A: shared helper")
    fork_b = fork_session(baseline_id, title="approach B: delegate to process_refund")
    print(f"\nForked {baseline_id} into {fork_a.session_id} and {fork_b.session_id}")

    print("\n=== Approach A ===\n")
    await run(APPROACH_A, fork_a.session_id)
    print("\n=== Approach B ===\n")
    await run(APPROACH_B, fork_b.session_id)
    print("\nNeither branch re-read the code, and neither knows the other exists.")


if __name__ == "__main__":
    asyncio.run(main())
