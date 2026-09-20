"""Checks for the refund workflow challenge.

Three things must be true:
  1. Every lookup_order and process_refund call happened after a verified
     get_customer, or was blocked.
  2. A multi-issue request produced a resolution that addresses every issue.
  3. Any escalation carries all four required fields.
"""

REQUIRED_HANDOFF_FIELDS = ["customer_id", "root_cause", "amount_usd", "recommended_action"]
ISSUES = {
    "damaged item": ["damag", "crack", "replace"],
    "billing mistake": ["charged twice", "duplicate", "refund"],
    "loyalty question": ["loyalty", "gold", "tier", "points"],
}


def print_check(final_text, blocked_calls, verified_ids, escalations):
    print("\nGate check")
    print("-" * 34)
    if len(verified_ids) > 0:
        print(f"  VERIFIED   {verified_ids}")
    else:
        print("  MISSING    no customer was ever verified")
    print(f"  BLOCKED    {len(blocked_calls)} call(s) stopped by the gate")
    gate_ok = len(verified_ids) > 0

    print("\nMulti-issue check")
    print("-" * 34)
    lowered = final_text.lower()
    covered = 0
    for issue in ISSUES:
        hit = False
        for word in ISSUES[issue]:
            if word in lowered:
                hit = True
        if hit:
            print(f"  ADDRESSED  {issue}")
            covered = covered + 1
        else:
            print(f"  MISSING    {issue}")
    issues_ok = covered == len(ISSUES)

    print("\nHandoff check")
    print("-" * 34)
    handoff_ok = True
    if len(escalations) == 0:
        print("  MISSING    nothing escalated, so the handoff was never tested")
        handoff_ok = False
    for ticket in escalations:
        for field in REQUIRED_HANDOFF_FIELDS:
            value = ticket.get(field)
            if value is None or value == "":
                print(f"  MISSING    {field}")
                handoff_ok = False
            else:
                print(f"  PRESENT    {field}")

    print("-" * 34)
    if gate_ok and issues_ok and handoff_ok:
        print("All three checks passed.")
    else:
        print("Not there yet. See the README checklist.")
    return gate_ok and issues_ok and handoff_ok
