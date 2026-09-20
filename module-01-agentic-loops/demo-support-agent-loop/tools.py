"""Mock backend for the Harbor Audio support agent.

In production these functions would call real services. Deterministic fakes
keep the demo predictable, fast, and free of side effects, so the only thing
on screen that varies is Claude's reasoning.

The seeded scenario: Priya sees what looks like a double charge on her
headphones order. The charge history shows one posted charge and one
authorization hold that was voided three days later. The agent has to find
that and explain it.
"""

CUSTOMERS = {
    "priya@harborlane.example": {
        "customer_id": "CUST-88412",
        "name": "Priya Raman",
        "account_status": "active",
    },
    "marco@garzafarms.example": {
        "customer_id": "CUST-90277",
        "name": "Marco Garza",
        "account_status": "active",
    },
}

ORDERS = {
    "CUST-88412": [
        {
            "order_id": "ORD-2481",
            "placed": "2026-07-14",
            "items": ["Harbor ANC-700 headphones", "USB-C cable (2m)"],
            "total_usd": 214.50,
            "charges": [
                {
                    "charge_id": "CHG-9931",
                    "amount_usd": 214.50,
                    "date": "2026-07-14",
                    "status": "posted",
                },
                {
                    "charge_id": "CHG-9932",
                    "amount_usd": 214.50,
                    "date": "2026-07-14",
                    "status": "authorization_voided",
                    "note": "Temporary card hold, released 2026-07-17",
                },
            ],
        },
        {
            "order_id": "ORD-2530",
            "placed": "2026-08-02",
            "items": ["Harbor desk stand"],
            "total_usd": 39.00,
            "charges": [
                {
                    "charge_id": "CHG-1044",
                    "amount_usd": 39.00,
                    "date": "2026-08-02",
                    "status": "posted",
                },
            ],
        },
    ],
    "CUST-90277": [
        {
            "order_id": "ORD-2555",
            "placed": "2026-08-10",
            "items": ["Harbor Mini speaker"],
            "total_usd": 89.00,
            "charges": [
                {
                    "charge_id": "CHG-1101",
                    "amount_usd": 89.00,
                    "date": "2026-08-10",
                    "status": "posted",
                },
            ],
        },
    ],
}


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
