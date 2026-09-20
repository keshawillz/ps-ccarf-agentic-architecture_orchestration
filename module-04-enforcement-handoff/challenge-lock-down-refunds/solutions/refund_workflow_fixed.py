"""Challenge solution: the refund workflow locked down.

Fix 1: a PreToolUse gate denies lookup_order and process_refund until a
       PostToolUse hook has recorded a verified customer ID.
Fix 2: the prompt tells the agent to list the issues first, investigate each
       one, and answer all of them in one reply.
Fix 3: the prompt names the four handoff fields and the tool schema already
       requires them, so a bare escalation cannot be submitted.

Run it from inside the solutions folder:
    cd solutions
    python refund_workflow_fixed.py
"""

import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

import sys
sys.path.append("..")
try:
    from workflow_check import print_check
except ImportError:
    sys.exit("Run from inside solutions/:\n    cd solutions\n    python refund_workflow_fixed.py")

from support_tools import (
    ALL_SUPPORT_TOOLS, GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND,
    SUPPORT_SERVER, ESCALATIONS, ledger,
)
MODEL = "claude-sonnet-5"

POLICY = """Harbor Audio support policy:
- Verify the customer with get_customer before any order lookup or refund.
- Refund duplicate charges in full.
- Refunds above 500 dollars require supervisor approval. Escalate them."""

SYSTEM_PROMPT = POLICY + """

You are a support agent for Harbor Audio. Follow the policy above.

When a message raises more than one issue, start by listing each issue on
its own line. Investigate every issue before you reply, then give one reply
that addresses all of them in order. Do not stop after the first one.

When you escalate, the human cannot see this conversation. Provide all four
fields: the customer_id, the root_cause as you understand it, the amount_usd
involved, and your recommended_action."""

# Dana gives her email and her customer ID. Both paths are open: the agent can
# verify properly with get_customer, or skip straight to lookup_order using the
# ID she typed. That choice is what the gate is there to remove.
QUESTION = (
    "This is Dana Okafor, dana@brightleaf.example, customer CUST-77103. "
    "Three things. My headphones order ORD-3312 got charged twice, refund "
    "CHG-5502. My studio monitors ORD-3340 arrived with a cracked cabinet, "
    "I want a full refund on those too. And does my gold tier get me "
    "anything here?"
)

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
    """PostToolUse on get_customer: remember IDs that were really verified."""
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
    """PreToolUse on lookup_order and process_refund: deny until verified."""
    if len(VERIFIED_IDS) == 0:
        BLOCKED.append(input_data["tool_name"])
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked: verify the customer with get_customer first."
                ),
            }
        }
    return {}


async def run():
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"support": SUPPORT_SERVER},
        allowed_tools=ALL_SUPPORT_TOOLS,
        hooks={
            "PostToolUse": [HookMatcher(matcher=GET_CUSTOMER, hooks=[record_verification])],
            "PreToolUse": [
                HookMatcher(matcher=LOOKUP_ORDER, hooks=[require_verification]),
                HookMatcher(matcher=PROCESS_REFUND, hooks=[require_verification]),
            ],
        },
        max_budget_usd=2.0,
    )
    final_text = ""
    async for message in query(prompt=QUESTION, options=options):
        if hasattr(message, "result"):
            final_text = message.result
    return final_text


async def main():
    print(f"Customer: {QUESTION}\n")
    final_text = await run()
    print("=" * 60)
    print(final_text)
    print("=" * 60)
    print("Ledger:", json.dumps(ledger()))
    print_check(final_text, BLOCKED, VERIFIED_IDS, ESCALATIONS)


if __name__ == "__main__":
    asyncio.run(main())
