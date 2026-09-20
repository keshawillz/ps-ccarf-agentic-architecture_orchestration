"""Audit log. Every state change should land here."""

LOG = []


def record(event, subject_id, note):
    LOG.append({"event": event, "subject_id": subject_id, "note": note})
