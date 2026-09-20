"""Challenge starter: add both hooks to the support agent.

This agent works, mostly. Two things are wrong:
  1. It reads raw tool output, so it sees Unix timestamps next to ISO strings
     and a status of "2", and has to guess what they mean.
  2. The 500 dollar refund limit is a sentence in the prompt. Nothing stops
     the refund tool from running above it.

Your job (see README.md):
  Task 1: add a PostToolUse hook that normalizes every date and status.
  Task 2: add a PreToolUse hook that denies refunds over 500 dollars and
          points the agent to escalation.
  Task 3: prove both fired by writing to hook_log.txt every time they run.

Run it:
    python support_agent.py
"""

import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

from messy_tools import ALL_SUPPORT_TOOLS, PROCESS_REFUND, SUPPORT_SERVER, ORDERS, ledger
from normalize import extract_text, normalize_record, rebuild_like

MODEL = "claude-sonnet-5"
REFUND_LIMIT_USD = 500.0
LOG_PATH = "hook_log.txt"

SYSTEM_PROMPT = """You are a support agent for Harbor Audio. Verify the customer
with get_customer first. Refund duplicate charges in full. If a tool refuses
a call, follow the reason it gives you."""

QUESTION = ("dana@brightleaf.example. Two things: when was each of my orders "
            "placed, and ORD-3340 got charged twice, CHG-5610 and CHG-5611, "
            "refund the duplicate.")


def log_hook(line):
    """Task 3 writes here. Right now nothing calls it."""
    with open(LOG_PATH, "a") as handle:
        handle.write(line + "\n")


async def main():
    open(LOG_PATH, "w").close()
    # Task 1 and Task 2 go here. hooks is empty in the starter.
    hooks = {}
    options = ClaudeAgentOptions(model=MODEL, system_prompt=SYSTEM_PROMPT,
                                 mcp_servers={"support": SUPPORT_SERVER},
                                 allowed_tools=ALL_SUPPORT_TOOLS, hooks=hooks, max_budget_usd=1.5)
    print(f"Customer: {QUESTION}\n")
    async for message in query(prompt=QUESTION, options=options):
        if hasattr(message, "result"):
            print(message.result)
    print("\nLedger:", json.dumps(ledger()))
    print("\nhook_log.txt:")
    with open(LOG_PATH) as handle:
        lines = handle.read().strip()
    if lines == "":
        print("  (empty: no hook fired)")
    else:
        print(lines)


if __name__ == "__main__":
    asyncio.run(main())
