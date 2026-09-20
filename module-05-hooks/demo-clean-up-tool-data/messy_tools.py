"""Support tools whose backends disagree on formats.

Real systems do this. One service returns Unix timestamps, another returns
ISO 8601 strings, a third uses bare status codes where the others use words.
This fixes it in a hook rather than in every tool.

Tool names on the wire are mcp__support__<name>.
"""

import json

from claude_agent_sdk import create_sdk_mcp_server, tool

CUSTOMERS = {
    "dana@brightleaf.example": {"customer_id": "CUST-77103", "name": "Dana Okafor",
                                "member_since": 1704067200},
}

# Same customer, three formats across two tools.
ORDERS = {
    "CUST-77103": [
        {"order_id": "ORD-3312", "placed": "2026-08-05T14:22:00Z",
         "total_usd": 214.50, "status_code": 2,
         "charges": [
             {"charge_id": "CHG-5501", "amount_usd": 214.50, "posted": 1785939720},
             {"charge_id": "CHG-5502", "amount_usd": 214.50, "posted": 1785939725},
         ]},
        {"order_id": "ORD-3340", "placed": "08/28/2026", "total_usd": 780.00,
         "status_code": 3,
         "charges": [{"charge_id": "CHG-5610", "amount_usd": 780.00,
                      "posted": 1787918400}]},
    ],
}

STATUS_WORDS = {1: "pending", 2: "delivered", 3: "shipped", 4: "cancelled"}
REFUNDS = {}
ESCALATIONS = []


def as_result(data):
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool("get_customer", "Look up a customer by email.", {"email": str})
async def get_customer(args):
    record = CUSTOMERS.get(args["email"].lower().strip())
    if record is None:
        return as_result({"found": False})
    return as_result({"found": True, "customer_id": record["customer_id"],
                      "name": record["name"], "member_since": record["member_since"]})


@tool("lookup_order", "Return orders and charges for a customer ID.", {"customer_id": str})
async def lookup_order(args):
    orders = ORDERS.get(args["customer_id"])
    if orders is None:
        return as_result({"found": False})
    return as_result({"found": True, "orders": orders})


@tool("process_refund", "Refund a posted charge in full.", {"charge_id": str, "reason": str})
async def process_refund(args):
    charge_id = args["charge_id"]
    for orders in ORDERS.values():
        for order in orders:
            for charge in order["charges"]:
                if charge["charge_id"] == charge_id and charge_id not in REFUNDS:
                    REFUNDS[charge_id] = "RFND-" + str(1000 + len(REFUNDS))
                    return as_result({"success": True, "refund_id": REFUNDS[charge_id],
                                      "amount_usd": charge["amount_usd"]})
    return as_result({"success": False, "message": "No refundable charge with that ID"})


@tool("escalate_to_human", "Hand the case to a human with full context.",
      {"customer_id": str, "root_cause": str, "amount_usd": float, "recommended_action": str})
async def escalate_to_human(args):
    ESCALATIONS.append(dict(args))
    return as_result({"success": True, "ticket_id": "ESC-" + str(500 + len(ESCALATIONS))})


SUPPORT_SERVER = create_sdk_mcp_server(
    name="support", tools=[get_customer, lookup_order, process_refund, escalate_to_human])

GET_CUSTOMER = "mcp__support__get_customer"
LOOKUP_ORDER = "mcp__support__lookup_order"
PROCESS_REFUND = "mcp__support__process_refund"
ESCALATE = "mcp__support__escalate_to_human"
ALL_SUPPORT_TOOLS = [GET_CUSTOMER, LOOKUP_ORDER, PROCESS_REFUND, ESCALATE]


def ledger():
    return {"refunds": dict(REFUNDS), "escalations": list(ESCALATIONS)}
