"""Challenge solution: the support agent with all three fixes in place.

Fix 1: stop_reason drives the loop. No keyword scanning.
Fix 2: the assistant turn goes into history untouched, and tool results go
       back as tool_result blocks tied to their tool_use_id.
Fix 3: MAX_TURNS is a tripwire that raises. It is never the normal exit.

Run it from inside the solutions folder:
    cd solutions
    python fixed_agent.py
"""

import json
import sys

import anthropic

# The shared mock backend (tools.py) lives one folder up. This line tells
# Python to also look there when importing.
sys.path.append("..")
try:
    from tools import get_customer, lookup_order, process_refund, refund_ledger
except ImportError:
    sys.exit(
        "Could not find tools.py. Run this file from inside the solutions "
        "folder:\n    cd solutions\n    python fixed_agent.py"
    )

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a support agent for Harbor Audio, an online \
electronics store. Use your tools to look up real account and order data. \
Verify who you are talking to with get_customer before discussing any order \
details. When a customer is owed money, process the refund yourself with \
process_refund. Keep a warm tone and reassure the customer that their issue \
is being resolved."""

TOOLS = [
    {
        "name": "get_customer",
        "description": (
            "Look up a customer record by email address. Returns the verified "
            "customer ID, name, and account status. Call this first, before "
            "any order operations, to confirm who you are talking to."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "The customer's email address"}
            },
            "required": ["email"],
        },
    },
    {
        "name": "lookup_order",
        "description": (
            "Return all orders for a verified customer, including items, "
            "totals, and the full charge history for each order. Requires a "
            "customer_id returned by get_customer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID from get_customer"}
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Refund a posted charge in full. Requires the exact charge_id "
            "from lookup_order and a short reason. Returns a refund "
            "confirmation with a refund_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "charge_id": {"type": "string", "description": "Charge ID, e.g. CHG-5502"},
                "reason": {"type": "string", "description": "Why the charge is being refunded"},
            },
            "required": ["charge_id", "reason"],
        },
    },
]

DEFAULT_QUESTION = (
    "Hi, I got billed twice for my headphones order this month. "
    "My email is dana@brightleaf.example. Please refund the extra charge."
)

# Fix 3: a real safety net. Ten turns is generous for this workflow. If the
# loop ever gets here, that's a bug worth investigating, so it raises
# instead of exiting quietly.
MAX_TURNS = 10


def run_tool(name, tool_input):
    """Run the Python function that matches a tool call from Claude."""
    if name == "get_customer":
        return get_customer(tool_input["email"])
    if name == "lookup_order":
        return lookup_order(tool_input["customer_id"])
    if name == "process_refund":
        return process_refund(tool_input["charge_id"], tool_input["reason"])
    raise ValueError(f"Claude asked for a tool we don't have: {name}")


def get_reply_text(response):
    """Gather all the text blocks in a response into one string."""
    text = ""
    for block in response.content:
        if block.type == "text":
            text += block.text
    return text


def run_agent(user_message):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]
    turn = 0

    while True:
        turn += 1
        if turn > MAX_TURNS:
            raise RuntimeError(
                f"Agent exceeded {MAX_TURNS} turns without reaching end_turn. "
                "The limit is a tripwire, so investigate before raising it."
            )

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        print(f"\n--- Turn {turn} | stop_reason: {response.stop_reason} ---")

        # Fix 2, part one: the assistant turn enters history exactly as
        # Claude produced it, thinking blocks and tool_use blocks included.
        messages.append({"role": "assistant", "content": response.content})

        # Fix 1: stop_reason is the only signal that decides what happens
        # next. The reply text plays no part in control flow.
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "thinking":
                    print("[thinking]")
                elif block.type == "text":
                    print(f"Claude: {block.text}")
                elif block.type == "tool_use":
                    print(f"Tool call: {block.name} with input {json.dumps(block.input)}")
                    result = run_tool(block.name, block.input)
                    print(f"Tool result: {json.dumps(result)}")
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                    tool_results.append(tool_result)
            # Fix 2, part two: the follow-up user message carries only
            # tool_result blocks. Nothing else rides along.
            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "end_turn":
            final_text = get_reply_text(response)
            print(f"Claude: {final_text}")
            return final_text

        raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")


# This block runs when you execute the file directly: python fixed_agent.py
if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = DEFAULT_QUESTION
    print(f"Customer: {question}")
    # finally makes sure the refund ledger prints even if the run errors out.
    try:
        run_agent(question)
    finally:
        print(f"\n{refund_ledger()}")
