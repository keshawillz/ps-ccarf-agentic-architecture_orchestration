"""Demo: Run subagents in parallel.

To run subagents at the same time, the coordinator emits all its Agent tool
calls in one response. Spread the same calls across separate turns and they
run one after another, because each turn has to finish before the next begins.

This demo logs the clock time of every spawn so you can see the difference
rather than infer it from a stopwatch.

Run it:
    python parallel_agents.py            both runs
    python parallel_agents.py parallel   parallel only
    python parallel_agents.py sequential sequential only
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

MODEL = "claude-sonnet-5"
SOURCES_PATH = "../sources"
AGENT_TOOL_NAMES = ["Agent", "Task"]
SUBAGENT_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + SUBAGENT_TOOLS

# background=True forces this subagent to run in the background, which is what
# lets several of them overlap. Since Claude Code v2.1.198 background is the
# default, so this line is belt and braces: it makes the intent visible in the
# code, and it keeps the demo behaving the same way on older versions.
POLICY_READER = AgentDefinition(
    description=(
        "Reads one named policy document and summarizes the rules it "
        "contains. Give it exactly one file name."
    ),
    prompt=f"""You read one policy document and summarize its rules.

The documents are in {SOURCES_PATH}. You will be told which single file to
read. Read only that file.

Return a short list of the rules it states, each with the page number it came
from. Keep it under 150 words.""",
    tools=SUBAGENT_TOOLS,
    model=MODEL,
    background=True,
)

PARALLEL_PROMPT = """Read all three policy documents.

Spawn three policy-reader subagents in a single response, one per file:
  harbor-returns-policy.md
  support-escalation-guide.md
  payment-processing-notes.md

Emit all three Agent tool calls in the same response so they run at the same
time. Do not wait for one to finish before starting the next.

When all three return, list the file names you covered."""

SEQUENTIAL_PROMPT = """Read all three policy documents.

Spawn one policy-reader subagent at a time. Wait for each one to return
before spawning the next. Use one Agent tool call per response, in this
order:
  harbor-returns-policy.md
  support-escalation-guide.md
  payment-processing-notes.md

When all three have returned, list the file names you covered."""


async def run_with_timing(label, prompt):
    """Run the coordinator and print the elapsed time at each spawn."""
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=(
            "You are a coordinator. Delegate reading to policy-reader "
            "subagents. Do not read the files yourself."
        ),
        allowed_tools=COORDINATOR_TOOLS,
        agents={"policy-reader": POLICY_READER},
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=2.0,
    )

    print(f"\n=== {label} ===")
    started = time.time()
    spawn_times = []

    async for message in query(prompt=prompt, options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        elapsed = time.time() - started
                        spawn_times.append(elapsed)
                        print(f"  spawn at t+{elapsed:6.1f}s")

    total = time.time() - started
    print(f"  total: {total:.1f}s across {len(spawn_times)} spawns")
    return spawn_times, total


async def main():
    if len(sys.argv) > 1:
        which = sys.argv[1]
    else:
        which = "both"

    if which == "parallel" or which == "both":
        await run_with_timing("Parallel: all calls in one response", PARALLEL_PROMPT)
    if which == "sequential" or which == "both":
        await run_with_timing("Sequential: one call per turn", SEQUENTIAL_PROMPT)

    print(
        "\nLook at the spawn times, not just the totals. In the parallel run "
        "the three spawns land within a second of each other. In the "
        "sequential run each one waits for the previous subagent to finish."
    )


if __name__ == "__main__":
    asyncio.run(main())
