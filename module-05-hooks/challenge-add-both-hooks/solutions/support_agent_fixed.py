"""Challenge solution: both hooks on the support agent.

Fix 1: PostToolUse normalizes every date and status via updatedToolOutput.
Fix 2: PreToolUse denies process_refund above 500 dollars with a reason
       that names the escalation path.
Fix 3: both hooks append a line to hook_log.txt, so the log is the proof.

Run it from inside the solutions folder:
    cd solutions
    python support_agent_fixed.py
"""

import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

from messy_tools import ALL_SUPPORT_TOOLS, PROCESS_REFUND, SUPPORT_SERVER, ORDERS, ledger
from normalize import normalize_record

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
    with open(LOG_PATH, "a") as handle:
        handle.write(line + "\n")


def amount_for(charge_id):
    for orders in ORDERS.values():
        for order in orders:
            for charge in order["charges"]:
                if charge["charge_id"] == charge_id:
                    return charge["amount_usd"]
    return 0.0


async def normalize_output(input_data, tool_use_id, context):
    """Fix 1: rewrite dates and statuses before Claude reads the result."""
    response = input_data.get("tool_response")
    if not isinstance(response, dict):
        return {}
    content = response.get("content", [])
    if len(content) == 0:
        return {}
    data = json.loads(content[0].get("text", "{}"))
    cleaned = normalize_record(data)
    log_hook("PostToolUse normalized " + input_data["tool_name"])
    new_response = {"content": [{"type": "text", "text": json.dumps(cleaned)}]}
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                   "updatedToolOutput": new_response}}


async def block_large_refund(input_data, tool_use_id, context):
    """Fix 2: deny any refund over the limit and point to escalation."""
    charge_id = input_data["tool_input"].get("charge_id", "")
    amount = amount_for(charge_id)
    if amount > REFUND_LIMIT_USD:
        log_hook(f"PreToolUse blocked refund {charge_id} at {amount:.2f} USD")
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Blocked: {amount:.2f} USD exceeds the {REFUND_LIMIT_USD:.0f} USD limit. "
                    "Escalate with escalate_to_human instead.")}}
    return {}


async def main():
    open(LOG_PATH, "w").close()
    hooks = {
        "PostToolUse": [HookMatcher(matcher="mcp__support__.*", hooks=[normalize_output])],
        "PreToolUse": [HookMatcher(matcher=PROCESS_REFUND, hooks=[block_large_refund])],
    }
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
