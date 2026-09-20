"""Format normalization used by the Module 5 hooks.

Plain functions, no SDK in here, so you can test them without an API key.
"""

from datetime import datetime, timezone

STATUS_WORDS = {1: "pending", 2: "delivered", 3: "shipped", 4: "cancelled"}


def to_iso_date(value):
    """Turn a Unix timestamp, an ISO string, or a US date into YYYY-MM-DD."""
    if isinstance(value, int):
        return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%d")
    if isinstance(value, str) and "T" in value:
        return value.split("T")[0]
    if isinstance(value, str) and value.count("/") == 2:
        month, day, year = value.split("/")
        return year + "-" + month + "-" + day
    return value


def normalize_record(data):
    """Walk a tool result and rewrite every date and status into one format."""
    if isinstance(data, dict):
        cleaned = {}
        for key in data:
            value = data[key]
            if key in ("placed", "posted", "member_since"):
                cleaned[key] = to_iso_date(value)
            elif key == "status_code":
                cleaned["status"] = STATUS_WORDS.get(value, "unknown")
            else:
                cleaned[key] = normalize_record(value)
        return cleaned
    if isinstance(data, list):
        cleaned = []
        for item in data:
            cleaned.append(normalize_record(item))
        return cleaned
    return data
