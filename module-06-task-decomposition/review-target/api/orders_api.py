"""HTTP handlers for orders. Part of the same pull request."""

from services.order_service import find_order


def get_order(request):
    order_id = request.get("order_id")
    if order_id is None:
        return {"status": 400, "error": "order_id is required"}
    order = find_order(order_id)
    if order is None:
        return {"status": 404, "error": "order not found"}
    return {"status": 200, "body": order}


def list_orders(request):
    customer_id = request.get("customer_id")
    orders = find_order(customer_id)
    return {"status": 200, "body": orders}
