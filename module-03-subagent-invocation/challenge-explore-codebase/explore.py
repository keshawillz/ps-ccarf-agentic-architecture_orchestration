"""Challenge starter: explore a codebase with parallel subagents.

You have an unfamiliar codebase in ../sample-app and two questions about it:
where the tests are, and how the refund path works.

This starter answers both questions badly:
  1. One general-purpose subagent handles everything, with every tool.
  2. It investigates one question, then the other, one turn at a time.
  3. Findings come back with no file paths, so nothing can be traced.

Your job (see README.md):
  Task 1: define two subagents, each with only the tools it needs.
  Task 2: spawn them in a single response so they run at the same time.
  Task 3: require a file path on every finding.

Run it:
    python explore.py
"""

import asyncio
import time

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

from findings_check import print_check

MODEL = "claude-sonnet-5"
APP_PATH = "../sample-app"
AGENT_TOOL_NAMES = ["Agent", "Task"]

# Every tool, handed to everybody. Task 1 is about narrowing this.
ALL_TOOLS = ["Glob", "Grep", "Read", "Write", "Edit", "Bash"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + ALL_TOOLS

# BUG 1: one generic subagent does both jobs. Nothing about it is specialized,
# its description gives the coordinator no basis for choosing between tasks,
# and it can write and run shell commands during what is supposed to be a
# read-only investigation.
EXPLORER = AgentDefinition(
    description="Looks at code and answers questions about it.",
    prompt="""You look at code and answer questions about it.

Use the tools available to find what you were asked about, then describe what
you found.""",
    tools=ALL_TOOLS,
    model=MODEL,
)

# BUG 2: this asks for one investigation, then the other. Each Agent call goes
# in its own response, so the second waits for the first to finish.
#
# BUG 3: nothing asks for file paths, so findings come back as prose and no
# claim can be traced to a location.
COORDINATOR_PROMPT = f"""You are exploring an unfamiliar codebase in {APP_PATH}.

Delegate to the explorer subagent. Do not read files yourself.

First, ask the explorer to find the test files and describe what they cover.
Wait for it to finish.

Then, ask the explorer to trace how process_refund works.

When both are done, write a short report describing what you learned."""


async def run_exploration():
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=(
            "You are a coordinator exploring a codebase. Delegate all file "
            "reading to subagents."
        ),
        allowed_tools=COORDINATOR_TOOLS,
        agents={"explorer": EXPLORER},
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
