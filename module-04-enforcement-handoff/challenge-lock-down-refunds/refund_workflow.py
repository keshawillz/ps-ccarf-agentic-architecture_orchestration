"""Challenge starter: lock down the refund workflow.

The support agent has a policy document, a system prompt that asks it to
follow the policy, and three problems:
  1. Verification lives only in the prompt, so a customer who volunteers IDs
     can talk the agent past it.
  2. A message with three separate problems gets a reply that handles one.
  3. Escalations arrive as a sentence. The human has no customer ID, no
     amount, no recommendation.

Your job (see README.md):
  Task 1: add a PreToolUse gate so lookup_order and process_refund are
          denied until get_customer has returned a verified ID.
  Task 2: make the agent split a multi-issue request, investigate each
          issue, and answer all of them.
  Task 3: make every escalation carry customer_id, root_cause, amount_usd,
          and recommended_action.

Run it:
    python refund_workflow.py
"""

import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

from support_tools import (
    ALL_SUPPORT_TOOLS, GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND,
    SUPPORT_SERVER, ESCALATIONS, ledger,
)
from workflow_check import print_check

MODEL = "claude-sonnet-5"

POLICY = """Harbor Audio support policy:
- Verify the customer with get_customer before any order lookup or refund.
- Refund duplicate charges in full.
- Refunds above 500 dollars require supervisor approval. Escalate them."""

# BUG 1: verification is a request, not a rule. There is no hook, so a
# customer who supplies their own IDs can skip get_customer entirely.
# BUG 2: nothing tells the agent to break a message into separate issues.
# BUG 3: nothing tells the agent what an escalation must contain, so it
# writes whatever feels natural, and the human gets a sentence.
SYSTEM_PROMPT = POLICY + """

You are a support agent for Harbor Audio. Follow the policy above. Be warm and
resolve what you can."""

## Dana gives her email and her customer ID. Both paths are open: the agent can
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


async def run():
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"support": SUPPORT_SERVER},
        allowed_tools=ALL_SUPPORT_TOOLS,
        hooks={},
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
