"""Charge lookup and state changes."""

CHARGES = {
    "CHG-5501": {"amount_usd": 214.50, "status": "posted"},
    "CHG-5502": {"amount_usd": 214.50, "status": "posted"},
    "CHG-6100": {"amount_usd": 89.00, "status": "authorization_voided"},
}


def find_charge(charge_id):
    return CHARGES.get(charge_id)


def mark_refunded(charge_id, reason):
    CHARGES[charge_id]["status"] = "refunded"
    return {"success": True, "charge_id": charge_id, "reason": reason}
