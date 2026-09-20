"""Challenge solution: explore a codebase with parallel subagents.

Fix 1: two specialized subagents, each with only the tools it needs.
Fix 2: both spawned in a single coordinator response, so they run at once.
Fix 3: every finding carries the file path it came from.

Run it from inside the solutions folder:
    cd solutions
    python explore_fixed.py
"""

import asyncio
import sys
import time

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

# findings_check.py lives one folder up.
sys.path.append("..")
try:
    from findings_check import print_check
except ImportError:
    sys.exit(
        "Could not find findings_check.py. Run this from inside the "
        "solutions folder:\n    cd solutions\n    python explore_fixed.py"
    )

MODEL = "claude-sonnet-5"
APP_PATH = "../sample-app"
AGENT_TOOL_NAMES = ["Agent", "Task"]

# Read-only tools. This is an investigation, so nothing here writes or runs
# anything. The coordinator holds the superset because subagents inherit their
# tools from the parent and can only narrow that set.
READ_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + READ_TOOLS

# Fix 1: two specialized subagents. Each description tells the coordinator
# exactly when to pick it, and each tool list is the minimum the job needs.
# Fix 3 lives here too: both prompts require a path on every finding.
TEST_FINDER = AgentDefinition(
    description=(
        "Finds test files in a codebase and describes what each one covers. "
        "Use for questions about testing, coverage, or which behavior is "
        "verified. Does not trace application logic."
    ),
    prompt="""You find test files and describe what they cover.

Use Glob to locate test files by name pattern, then Read them.

Return one block per test file:

  PATH: the file path, relative to the folder you were given
  COVERS: what this file tests, in one sentence
  CASES: the test function names in the file

The PATH field is required on every block. A finding without a path cannot be
checked by the person reading your report.""",
    tools=READ_TOOLS,
    model=MODEL,
)

REFUND_TRACER = AgentDefinition(
    description=(
        "Traces a function through the codebase, following its imports and "
        "call chain. Use for questions about how a code path works. Does not "
        "inventory test files."
    ),
    prompt="""You trace a function through a codebase.

Start with Grep to find where the function is defined, then Read that file and
follow its imports to every function it calls.

Return one block per function in the chain:

  PATH: the file path where this function lives
  FUNCTION: the function name
  ROLE: what it does in one sentence, and what it calls next

The PATH field is required on every block. A trace without paths is a story,
not a finding.""",
    tools=READ_TOOLS,
    model=MODEL,
)

# Fix 2: both Agent calls go in one response, so the two investigations run at
# the same time instead of one waiting on the other.
COORDINATOR_PROMPT = f"""You are exploring an unfamiliar codebase in {APP_PATH}.

Delegate to your subagents. Do not read files yourself.

Spawn both of these in a single response, so they run at the same time:
  - test-finder, to inventory the test files and what they cover
  - refund-tracer, to trace process_refund through its whole call chain

Emit both Agent tool calls in the same response. Do not wait for one to return
before starting the other.

When both return, write a short report. Keep the PATH value on every finding
exactly as the subagent reported it."""


async def run_exploration():
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=(
            "You are a coordinator exploring a codebase. Delegate all file "
            "reading to subagents."
        ),
        allowed_tools=COORDINATOR_TOOLS,
        agents={
            "test-finder": TEST_FINDER,
            "refund-tracer": REFUND_TRACER,
        },
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=3.0,
    )

    started = time.time()
    spawn_log = []
    report = ""

    async for message in query(prompt=COORDINATOR_PROMPT, options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        elapsed = time.time() - started
                        spawn_log.append(elapsed)
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  spawn at t+{elapsed:6.1f}s  ->  {which}")
        if hasattr(message, "result"):
            report = message.result

    return report, spawn_log


async def main():
    print(f"Exploring: {APP_PATH}\n")
    print("Delegation log:")
    report, spawn_log = await run_exploration()
    print("\n" + "=" * 60)
    print(report)
    print_check(report, spawn_log)


if __name__ == "__main__":
    asyncio.run(main())
