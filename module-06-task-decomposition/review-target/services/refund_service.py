"""Refund business logic."""

from services.audit import record

CHARGES = {"CHG-5501": {"amount_usd": 214.50, "status": "posted"}}
SUPERVISOR_LIMIT_USD = 500.0


def lookup_charge(charge_id):
    return CHARGES.get(charge_id)


def issue_refund(charge_id, reason):
    charge = CHARGES[charge_id]
    if charge["amount_usd"] > SUPERVISOR_LIMIT_USD:
        raise ValueError("supervisor approval required")
    charge["status"] = "refunded"
    record("refund", charge_id, reason)
    return {"refunded": charge_id, "amount_usd": charge["amount_usd"]}
