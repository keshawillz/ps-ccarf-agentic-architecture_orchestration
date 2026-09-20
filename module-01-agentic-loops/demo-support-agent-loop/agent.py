"""Demo: Build and run an agentic loop with the Claude API.

The whole pattern fits in one function:

    1. Send the conversation to Claude, with tools attached.
    2. Inspect stop_reason.
    3. If it's "tool_use", run the requested tools, append the results
       to the conversation, and go around again.
    4. If it's "end_turn", Claude is done. Return the answer.

Nothing in this file tells Claude which tool to call or in what order.
That decision happens inside the model, based on the conversation history.

Run it:
    python agent.py
    python agent.py "your own support question here"
"""

import json
import sys

import anthropic

from tools import get_customer, lookup_order

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a support agent for Harbor Audio, an online \
electronics store. Use your tools to look up real account and order data \
before answering. Verify who you are talking to with get_customer before \
discussing any order details. Be concise, explain what you found, and \
resolve the issue when you can."""

# Tool schemas: the description is what Claude reads when deciding which
# tool fits. 
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
                "email": {
                    "type": "string",
                    "description": "The customer's email address",
                }
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
                "customer_id": {
                    "type": "string",
                    "description": "Customer ID from get_customer, e.g. CUST-88412",
                }
            },
            "required": ["customer_id"],
        },
    },
]

# The messy billing question. Vague on purpose: no order number,
# no dates, just "the big one with the headphones."
DEFAULT_QUESTION = (
    "Hi, I think you charged me twice last month? It was the big order, "
    "the one with the headphones. My email is priya@harborlane.example. "
    "Can you sort this out?"
)


def run_tool(name, tool_input):
    """Run the Python function that matches a tool call from Claude.

    Claude sends back the tool's name plus a dict of inputs. This function
    turns that into a real function call.
    """
    if name == "get_customer":
        return get_customer(tool_input["email"])
    if name == "lookup_order":
        return lookup_order(tool_input["customer_id"])
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
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,  # covers thinking plus response text on Sonnet 5
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        print(f"\n--- Turn {turn} | stop_reason: {response.stop_reason} ---")

        # The assistant turn goes into history exactly as Claude produced it,
        # thinking blocks and all. This history is everything Claude knows
        # on the next iteration.
        messages.append({"role": "assistant", "content": response.content})

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
            # The follow-up user message carries only tool_result blocks.
            # Extra text here can end the turn early or error on server tools.
            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "end_turn":
            final_text = get_reply_text(response)
            print(f"Claude: {final_text}")
            return final_text

        # Anything else means the loop can't safely continue on its own.
        # The full set: max_tokens, refusal, pause_turn,
        # stop_sequence, and model_context_window_exceeded each need their
        # own handling in a production loop.
        raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")


# This block runs when you execute the file directly: python agent.py
if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = DEFAULT_QUESTION
    print(f"Customer: {question}")
    run_agent(question)
