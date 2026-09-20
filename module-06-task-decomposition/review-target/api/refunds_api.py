"""HTTP handlers for refunds. Part of a pull request under review."""

from services.refund_service import issue_refund, lookup_charge


def post_refund(request):
    charge_id = request.get("charge_id")
    if charge_id is None:
        return {"status": 400, "error": "charge_id is required"}
    charge = lookup_charge(charge_id)
    if charge is None:
        return {"status": 404, "error": "charge not found"}
    result = issue_refund(charge_id, request.get("reason", ""))
    return {"status": 200, "body": result}


def get_refund_status(request):
    charge_id = request.get("charge_id")
    charge = lookup_charge(charge_id)
    return {"status": 200, "body": charge}
