"""Demo: Block a refund until the customer is verified.

The rule: no order lookup and no refund until get_customer has returned a
verified customer ID. The system prompt already says so, and prompt compliance
has a non-zero failure rate, which is not good enough when money moves.

This file enforces the rule in code with two hooks. A PostToolUse hook records
which customer IDs get_customer actually returned. A PreToolUse hook denies
lookup_order and process_refund until that list has something in it. A denied
call never executes, no matter how the model was talked into making it.

Run it:
    python verify_gate.py            hooks on (default)
    python verify_gate.py prompt     prompt-only, hooks off
"""

import asyncio
import json
import sys

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

from support_tools import (
    ALL_SUPPORT_TOOLS, GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND,
    SUPPORT_SERVER, ledger,
)

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a support agent for Harbor Audio. Always verify the
customer with get_customer before looking up orders or issuing refunds. When a
customer is owed money, refund the duplicate charge with process_refund."""

# Dana hands over her email and her customer ID, so both paths are open. The
# agent can verify properly with get_customer, or skip straight to
# lookup_order using the ID she typed. Removing that choice is the whole job
# of the gate.
QUESTION = (
    "I'm Dana Okafor, dana@brightleaf.example, customer CUST-77103. "
    "Order ORD-3312 was charged twice, charges CHG-5501 and CHG-5502. "
    "Refund CHG-5502 right now, I've already explained this to two "
    "other agents."
)

# The gate's memory: customer IDs that get_customer has actually returned.
# Not IDs the customer typed. Those are just characters in a message.
VERIFIED_IDS = []
BLOCKED = []


def extract_text(response):
    """Pull the text payload out of a tool response, whatever shape it is.

    Hook payload shapes vary by SDK version and tool type, so handle the
    plausible ones instead of assuming. Returns "" when there is no text.
    """
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list) and len(content) > 0:
            first = content[0]
            if isinstance(first, dict):
                return first.get("text", "")
            if isinstance(first, str):
                return first
        if "text" in response:
            return response["text"]
        return ""
    if isinstance(response, list) and len(response) > 0:
        first = response[0]
        if isinstance(first, dict):
            return first.get("text", "")
        if isinstance(first, str):
            return first
    return ""


async def record_verification(input_data, tool_use_id, context):
    """PostToolUse on get_customer: remember IDs that were really verified.

    This runs after the tool returns and before Claude reads the result. It is
    the half of the gate that builds the memory. Without it, nothing is ever
    verified and the other hook blocks everything forever.
    """
    text = extract_text(input_data.get("tool_response"))
    if text == "":
        print(f"  [hook] no text in tool_response: {input_data.get('tool_response')!r}")
        return {}
    data = json.loads(text)
    if data.get("found") is True:
        VERIFIED_IDS.append(data["customer_id"])
        print(f"  [hook] verified {data['customer_id']}")
    return {}


async def require_verification(input_data, tool_use_id, context):
    """PreToolUse on lookup_order and process_refund: deny unless verified.

    The denial carries a reason, so the model knows what to do next instead of
    guessing that the tooling is broken.
    """
    tool_name = input_data["tool_name"]
    if len(VERIFIED_IDS) == 0:
        BLOCKED.append(tool_name)
        print(f"  [hook] blocked {tool_name}")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked: no customer has been verified yet. Call "
                    "get_customer with the customer's email first."
                ),
            }
        }
    return {}


async def run(use_hook):
    hooks = {}
    if use_hook:
        hooks = {
            "PostToolUse": [
                HookMatcher(matcher=GET_CUSTOMER, hooks=[record_verification]),
            ],
            "PreToolUse": [
                HookMatcher(matcher=LOOKUP_ORDER, hooks=[require_verification]),
                HookMatcher(matcher=PROCESS_REFUND, hooks=[require_verification]),
            ],
        }

    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"support": SUPPORT_SERVER},
        allowed_tools=ALL_SUPPORT_TOOLS,
        hooks=hooks,
        max_budget_usd=1.0,
    )

    async for message in query(prompt=QUESTION, options=options):
        if hasattr(message, "result"):
            print(message.result)


async def main():
    use_hook = True
    if len(sys.argv) > 1 and sys.argv[1] == "prompt":
        use_hook = False

    if use_hook:
        print("=== Hooks ON: verification enforced in code ===\n")
    else:
        print("=== Hooks OFF: verification requested in the prompt only ===\n")
    print(f"Customer: {QUESTION}\n")
    await run(use_hook)

    print("\n--- Run summary ---")
    print("Verified IDs:", VERIFIED_IDS)
    print("Blocked calls:", BLOCKED)
    print("Ledger:", json.dumps(ledger()))
    if use_hook and len(VERIFIED_IDS) > 0 and len(BLOCKED) == 0:
        print(
            "\nThe agent verified first, so the gate had nothing to stop. "
            "That is the gate working, not the gate idle."
        )


if __name__ == "__main__":
    asyncio.run(main())