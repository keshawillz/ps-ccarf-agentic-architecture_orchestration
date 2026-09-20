"""Challenge starter: a support agent with a broken loop.

Symptoms reported from "production":
  1. The agent sometimes announces a refund and exits before the refund
     actually runs.
  2. It repeats tool calls it already made and loses track of results.
  3. When it goes wrong, it goes wrong expensively.

Your job (see README.md):
  Task 1: make stop_reason drive the loop.
  Task 2: feed tool results back correctly.
  Task 3: add a retry limit as a safety net that fails loudly.

Run it:
    python broken_agent.py
"""

import json
import sys

import anthropic

from tools import get_customer, lookup_order, process_refund, refund_ledger

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

# LAB GUARD: this exists so a runaway loop in the lab can't spend money
# forever. It is set absurdly high and it is NOT the safety net Task 3 asks
# for. When your fix is in place, the loop should never get anywhere near it.
LAB_GUARD_MAX_CALLS = 25


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
    calls = 0

    while True:
        calls += 1
        if calls > LAB_GUARD_MAX_CALLS:
            sys.exit("LAB GUARD tripped: too many API calls. Something is wrong.")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        reply_text = get_reply_text(response)
        if reply_text != "":
            print(f"Claude: {reply_text}")

        # BUG: the loop decides Claude is finished by scanning the reply
        # text for a keyword. A turn can contain reassuring text AND a
        # pending tool call at the same time. When it does, this exits
        # before the tool ever runs.
        if "resolved" in reply_text.lower():
            print("\nAgent says the case is resolved. Exiting.")
            return reply_text

        # BUG: only the text of Claude's reply goes into history. The
        # tool_use blocks are thrown away, and tool output goes back as a
        # plain chat message instead of tool_result blocks tied to a
        # tool_use_id. Claude can't see what it called or what came back.
        if reply_text == "":
            messages.append({"role": "assistant", "content": "(working)"})
        else:
            messages.append({"role": "assistant", "content": reply_text})

        tool_notes = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"Tool call: {block.name} with input {json.dumps(block.input)}")
                result = run_tool(block.name, block.input)
                print(f"Tool result: {json.dumps(result)}")
                tool_notes.append(f"Tool output from {block.name}: {json.dumps(result)}")

        if len(tool_notes) > 0:
            messages.append({"role": "user", "content": "\n".join(tool_notes)})
        else:
            messages.append({"role": "user", "content": "Please continue."})


# This block runs when you execute the file directly: python broken_agent.py
if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = DEFAULT_QUESTION
    print(f"Customer: {question}\n")
    # finally makes sure the refund ledger prints even if the run errors out.
    try:
        run_agent(question)
    finally:
        print(f"\n{refund_ledger()}")
