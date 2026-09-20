"""Demo, second half: fork a session to branch from a shared baseline.

Parallel spawning runs several subagents at once from the same coordinator.
Forking is a different move: you pay for one expensive analysis, then branch
that finished conversation into independent lines of work.

Both branches start knowing everything the baseline learned. Neither branch
can see the other.

Note the contrast with everything else in this module. A normal subagent
starts with an empty context. A fork starts with the parent's conversation,
which is why it is the exception on the "what crosses the boundary" slide.

Run it:
    python fork_baseline.py
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

MODEL = "claude-sonnet-5"
APP_PATH = "../sample-app"

BASELINE_TASK = f"""Read the code in {APP_PATH} yourself and build an
understanding of how refunds work. Trace process_refund from its entry point
through every function it calls, and note where the policy limits are
enforced.

Summarize what you found in under 200 words. This summary is the baseline for
further work, so be precise about file names and function names."""

BRANCH_ONE = """Based on the refund code you just analyzed, propose a testing
strategy built around unit tests for each function in isolation. Keep it under
120 words."""

BRANCH_TWO = """Based on the refund code you just analyzed, propose a testing
strategy built around integration tests that exercise the whole refund path.
Keep it under 120 words."""


def make_options(resume_id=None, fork=False):
    options = ClaudeAgentOptions(
        model=MODEL,
        allowed_tools=["Glob", "Grep", "Read"],
        # The baseline has to do the reading itself, in its own transcript.
        # If it delegates to a background subagent, the analysis lives in the
        # subagent's session, and a fork of the baseline inherits nothing.
        disallowed_tools=["Agent", "Task"],
        max_budget_usd=2.0,
    )
    if resume_id is not None:
        options.resume = resume_id
        options.fork_session = fork
    return options


async def print_response(client):
    """Print what the model says, and say so if it errors or says nothing."""
    session_id = None
    said_something = False
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip() != "":
                    print(block.text)
                    said_something = True
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            if message.is_error:
                print(f"  [error] {message.result}")
    if not said_something:
        print("  (no text came back from this session)")
    return session_id


async def main():
    # Step 1: the expensive part. Read the code once.
    print("=== Baseline: analyzing the refund code ===")
    async with ClaudeSDKClient(options=make_options()) as client:
        await client.query(BASELINE_TASK)
        baseline_id = await print_response(client)

    print(f"\nBaseline session id: {baseline_id}")

    # Step 2: two forks from that finished conversation. Each one already
    # knows the analysis. Neither one repeats it, and neither sees the other.
    print("\n=== Branch A: unit testing strategy ===")
    async with ClaudeSDKClient(
        options=make_options(resume_id=baseline_id, fork=True)
    ) as client:
        await client.query(BRANCH_ONE)
        await print_response(client)

    print("\n=== Branch B: integration testing strategy ===")
    async with ClaudeSDKClient(
        options=make_options(resume_id=baseline_id, fork=True)
    ) as client:
        await client.query(BRANCH_TWO)
        await print_response(client)

    print(
        "\nNeither branch re-read the code. Both inherited the baseline "
        "analysis, and neither one knows the other branch exists."
    )


if __name__ == "__main__":
    asyncio.run(main())