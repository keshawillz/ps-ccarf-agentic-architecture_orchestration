"""Order business logic."""

from services.audit import record

ORDERS = {"ORD-3312": {"customer_id": "CUST-77103", "total_usd": 214.50}}


def find_order(order_id):
    order = ORDERS.get(order_id)
    record("order_lookup", order_id, "")
    return order
