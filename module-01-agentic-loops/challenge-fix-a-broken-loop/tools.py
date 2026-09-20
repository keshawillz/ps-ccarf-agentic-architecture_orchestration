"""Mock backend for the challenge agent.

The seeded scenario: Dana really was charged twice for order ORD-3312.
Both charges posted. The correct resolution is a refund of the duplicate
charge CHG-5502 through process_refund.

State lives in module-level dicts, so a refund sticks for the life of the
process and refunding the same charge twice returns an error.
"""

import json

CUSTOMERS = {
    "dana@brightleaf.example": {
        "customer_id": "CUST-77103",
        "name": "Dana Okafor",
        "account_status": "active",
    },
}

ORDERS = {
    "CUST-77103": [
        {
            "order_id": "ORD-3312",
            "placed": "2026-08-05",
            "items": ["Harbor ANC-700 headphones"],
            "total_usd": 214.50,
            "charges": [
                {
                    "charge_id": "CHG-5501",
                    "amount_usd": 214.50,
                    "date": "2026-08-05",
                    "status": "posted",
                },
                {
                    "charge_id": "CHG-5502",
                    "amount_usd": 214.50,
                    "date": "2026-08-05",
                    "status": "posted",
                },
            ],
        },
    ],
}

# Tracks every refund processed during this run: charge_id -> refund_id.
REFUNDS = {}


def get_customer(email):
    """Look up a customer record by email address."""
    record = CUSTOMERS.get(email.lower().strip())
    if record is None:
        return {"found": False, "message": f"No customer with email {email}"}
    return {
        "found": True,
        "customer_id": record["customer_id"],
        "name": record["name"],
        "account_status": record["account_status"],
    }


def lookup_order(customer_id):
    """Return all orders and charge history for a verified customer ID."""
    orders = ORDERS.get(customer_id)
    if orders is None:
        return {"found": False, "message": f"No orders for customer {customer_id}"}
    return {"found": True, "orders": orders}


def process_refund(charge_id, reason):
    """Refund a posted charge in full. Returns a refund confirmation."""
    if charge_id in REFUNDS:
        return {
            "success": False,
            "message": f"Charge {charge_id} was already refunded ({REFUNDS[charge_id]}).",
        }
    # Search every order's charge list for this charge ID.
    for orders in ORDERS.values():
        for order in orders:
            for charge in order["charges"]:
                if charge["charge_id"] == charge_id:
                    if charge["status"] != "posted":
                        return {
                            "success": False,
                            "message": f"Charge {charge_id} is not a posted charge.",
                        }
                    refund_id = f"RFND-{1000 + len(REFUNDS)}"
                    REFUNDS[charge_id] = refund_id
                    charge["status"] = "refunded"
                    return {
                        "success": True,
                        "refund_id": refund_id,
                        "charge_id": charge_id,
                        "amount_usd": charge["amount_usd"],
                        "reason": reason,
                    }
    return {"success": False, "message": f"No charge with ID {charge_id}"}


def refund_ledger():
    """Used by the run scripts to show what actually happened."""
    if len(REFUNDS) == 0:
        return "Refund ledger: EMPTY. No refunds were processed."
    return "Refund ledger: " + json.dumps(REFUNDS)
