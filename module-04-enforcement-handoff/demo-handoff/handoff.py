"""Demo: Escalate with a useful handoff.

The human receiving an escalation cannot see the conversation. Everything they
know about the case has to be in the handoff. This demo runs a case that has
to escalate (a refund over the supervisor threshold) and prints the ticket the
human would actually receive.

Run it:
    python handoff.py            structured handoff (default)
    python handoff.py bare       the "customer is upset" version, for contrast
"""

import asyncio
import json
import sys

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool

from support_tools import (
    ALL_SUPPORT_TOOLS, SUPPORT_SERVER, ESCALATIONS, ledger,
    get_customer, lookup_order, process_refund,
)

MODEL = "claude-sonnet-5"

# A bare escalation tool, kept only to show what the human gets without
# structure. Compare its schema to escalate_to_human in support_tools.py.
BARE_ESCALATIONS = []


@tool("escalate_to_human", "Hand the case to a human agent.", {"note": str})
async def escalate_bare(args):
    BARE_ESCALATIONS.append({"note": args["note"]})
    return {"content": [{"type": "text", "text": json.dumps({"success": True})}]}


BARE_SERVER = create_sdk_mcp_server(
    name="support", tools=[get_customer, lookup_order, process_refund, escalate_bare]
)

SYSTEM_PROMPT = """You are a support agent for Harbor Audio. Verify the customer
with get_customer first. Refunds above 500 dollars need supervisor approval,
which you cannot give, so escalate those to a human with escalate_to_human."""

QUESTION = (
    "Hi, it's dana@brightleaf.example. My studio monitors arrived with a "
    "cracked cabinet. I want a full refund on that order."
)


async def run(structured):
    if structured:
        server = SUPPORT_SERVER
    else:
        server = BARE_SERVER
    options = ClaudeAgentOptions(
        model=MODEL, system_prompt=SYSTEM_PROMPT,
        mcp_servers={"support": server}, allowed_tools=ALL_SUPPORT_TOOLS,
        max_budget_usd=1.0,
    )
    async for message in query(prompt=QUESTION, options=options):
        if hasattr(message, "result"):
            print(message.result)


async def main():
    structured = True
    if len(sys.argv) > 1 and sys.argv[1] == "bare":
        structured = False
    if structured:
        print("=== Structured handoff ===")
    else:
        print("=== Bare handoff ===")
    print(f"\nCustomer: {QUESTION}\n")
    await run(structured)
    print("\n--- What the human receives ---")
    if structured:
        print(json.dumps(ESCALATIONS, indent=2))
    else:
        print(json.dumps(BARE_ESCALATIONS, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
