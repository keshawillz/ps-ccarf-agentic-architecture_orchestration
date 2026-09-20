"""Refund processing for the Harbor Audio store."""

from billing.charges import find_charge, mark_refunded
from billing.limits import needs_supervisor


def process_refund(charge_id, reason):
    """Refund a posted charge in full."""
    charge = find_charge(charge_id)
    if charge is None:
        return {"success": False, "message": "No such charge"}
    if charge["status"] != "posted":
        return {"success": False, "message": "Charge is not posted"}
    if needs_supervisor(charge["amount_usd"]):
        return {"success": False, "message": "Supervisor approval required"}
    return mark_refunded(charge_id, reason)


def partial_refund(charge_id, percent, reason):
    """Refund part of a posted charge."""
    charge = find_charge(charge_id)
    if charge is None:
        return {"success": False, "message": "No such charge"}
    amount = charge["amount_usd"] * percent / 100
    if needs_supervisor(amount):
        return {"success": False, "message": "Supervisor approval required"}
    return mark_refunded(charge_id, reason)
