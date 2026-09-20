"""Policy limits for billing operations."""

SUPERVISOR_THRESHOLD_USD = 500.0


def needs_supervisor(amount_usd):
    return amount_usd > SUPERVISOR_THRESHOLD_USD
