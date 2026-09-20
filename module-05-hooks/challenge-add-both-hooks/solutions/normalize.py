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

# --- Hook payload helpers ---------------------------------------------------
# Hook payload shapes vary by SDK version and tool type. These two functions
# let a PostToolUse hook read a tool result and write a replacement without
# guessing the shape. Import them into your hook.


def extract_text(response):
    """Pull the text payload out of a tool response, whatever shape it is.

    Returns "" when there is no text, so the caller can bail out loudly.
    """
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list) and len(content) > 0:
            first = content[0]
            if isinstance(first, dict):
                return first.get("text", "")
            if isinstance(first, str):
                return first
        if "text" in response:
            return response["text"]
        return ""
    if isinstance(response, list) and len(response) > 0:
        first = response[0]
        if isinstance(first, dict):
            return first.get("text", "")
        if isinstance(first, str):
            return first
    return ""


def rebuild_like(original, new_text):
    """Put new_text back into the same shape the original response used.

    updatedToolOutput replaces what Claude reads, and it has to look like what
    the tool would have returned. Mirror the incoming shape instead of guessing.
    """
    if isinstance(original, str):
        return new_text
    if isinstance(original, dict):
        content = original.get("content")
        if isinstance(content, str):
            return {"content": new_text}
        if isinstance(content, list) and len(content) > 0:
            first = content[0]
            if isinstance(first, dict):
                return {"content": [{"type": "text", "text": new_text}]}
            return {"content": [new_text]}
        if "text" in original:
            return {"text": new_text}
    if isinstance(original, list) and len(original) > 0:
        if isinstance(original[0], dict):
            return [{"type": "text", "text": new_text}]
        return [new_text]
    return {"content": [{"type": "text", "text": new_text}]}