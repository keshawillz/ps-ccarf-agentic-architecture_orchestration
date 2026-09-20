"""The Harbor Audio support backend as Agent SDK tools.

Module 1 called these as plain Python functions from a hand-written loop.
Here they become SDK tools so the SDK's loop can call them, and so hooks in
Modules 4 and 5 can intercept them.

Tool names on the wire are mcp__support__<name>, which is the string hook
matchers and allowed_tools use.
"""

import json

from claude_agent_sdk import create_sdk_mcp_server, tool

SERVER = "support"

CUSTOMERS = {
    "dana@brightleaf.example": {
        "customer_id": "CUST-77103",
        "name": "Dana Okafor",
        "loyalty_tier": "gold",
    },
}

ORDERS = {
    "CUST-77103": [
        {
            "order_id": "ORD-3312",
            "items": ["Harbor ANC-700 headphones"],
            "total_usd": 214.50,
            "charges": [
                {"charge_id": "CHG-5501", "amount_usd": 214.50, "status": "posted"},
                {"charge_id": "CHG-5502", "amount_usd": 214.50, "status": "posted"},
            ],
        },
        {
            "order_id": "ORD-3340",
            "items": ["Harbor studio monitor pair"],
            "total_usd": 780.00,
            "charges": [
                {"charge_id": "CHG-5610", "amount_usd": 780.00, "status": "posted"},
            ],
        },
    ],
}

REFUNDS = {}
ESCALATIONS = []


def as_result(data):
    """Wrap a Python dict as the text content an SDK tool returns."""
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "get_customer",
    "Look up a customer by email. Returns the verified customer ID, name, and "
    "loyalty tier. Call this first, before any order operation.",
    {"email": str},
)
async def get_customer(args):
    record = CUSTOMERS.get(args["email"].lower().strip())
    if record is None:
        return as_result({"found": False, "message": "No customer with that email"})
    return as_result({"found": True, "customer_id": record["customer_id"],
                      "name": record["name"], "loyalty_tier": record["loyalty_tier"]})


@tool(
    "lookup_order",
    "Return all orders and charge history for a verified customer ID.",
    {"customer_id": str},
)
async def lookup_order(args):
    orders = ORDERS.get(args["customer_id"])
    if orders is None:
        return as_result({"found": False, "message": "No orders for that customer"})
    return as_result({"found": True, "orders": orders})


@tool(
    "process_refund",
    "Refund a posted charge in full. Requires the exact charge_id and a reason.",
    {"charge_id": str, "reason": str},
)
async def process_refund(args):
    charge_id = args["charge_id"]
    if charge_id in REFUNDS:
        return as_result({"success": False, "message": "Already refunded"})
    for orders in ORDERS.values():
        for order in orders:
            for charge in order["charges"]:
                if charge["charge_id"] == charge_id and charge["status"] == "posted":
                    refund_id = "RFND-" + str(1000 + len(REFUNDS))
                    REFUNDS[charge_id] = refund_id
                    charge["status"] = "refunded"
                    return as_result({"success": True, "refund_id": refund_id,
                                      "amount_usd": charge["amount_usd"]})
    return as_result({"success": False, "message": "No posted charge with that ID"})


@tool(
    "escalate_to_human",
    "Hand the case to a human agent. The human cannot see this conversation, "
    "so every field is required: customer_id, root_cause, amount_usd, and "
    "recommended_action.",
    {"customer_id": str, "root_cause": str, "amount_usd": float, "recommended_action": str},
)
async def escalate_to_human(args):
    ticket = {"ticket_id": "ESC-" + str(500 + len(ESCALATIONS)),
              "customer_id": args["customer_id"], "root_cause": args["root_cause"],
              "amount_usd": args["amount_usd"], "recommended_action": args["recommended_action"]}
    ESCALATIONS.append(ticket)
    return as_result({"success": True, "ticket_id": ticket["ticket_id"]})


SUPPORT_SERVER = create_sdk_mcp_server(
    name=SERVER,
    tools=[get_customer, lookup_order, process_refund, escalate_to_human],
)

# Full wire names, for allowed_tools and for hook matchers.
GET_CUSTOMER = "mcp__support__get_customer"
LOOKUP_ORDER = "mcp__support__lookup_order"
PROCESS_REFUND = "mcp__support__process_refund"
ESCALATE = "mcp__support__escalate_to_human"
ALL_SUPPORT_TOOLS = [GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND, ESCALATE]


def ledger():
    """What actually happened this run, for the checks at the end."""
    return {"refunds": dict(REFUNDS), "escalations": list(ESCALATIONS)}
