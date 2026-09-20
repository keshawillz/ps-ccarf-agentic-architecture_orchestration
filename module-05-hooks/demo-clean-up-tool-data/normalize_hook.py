"""Clip 2: Clean up tool data with PostToolUse.

The backends return dates three ways and order status as a bare number. A
PostToolUse hook runs after each tool returns and before Claude reads the
result, so one function fixes every tool at once. The hook replaces the tool
output with updatedToolOutput.

Run it:
    python normalize_hook.py         hook on
    python normalize_hook.py raw     hook off, see what Claude gets otherwise
"""

import asyncio
import json
import sys

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

from messy_tools import ALL_SUPPORT_TOOLS, SUPPORT_SERVER
from normalize import normalize_record, rebuild_like, extract_text

MODEL = "claude-sonnet-5"
QUESTION = "Email dana@brightleaf.example. When did each of my orders get placed, and what's the status of each?"

async def normalize_output(input_data, tool_use_id, context):
    """Rewrite every date and status in the tool result before Claude sees it."""
    response = input_data.get("tool_response")
    text = extract_text(response)
    if text == "":
        print(f"  [hook] no text in tool_response: {response!r}"[:200])
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"  [hook] tool_response was not JSON: {text[:80]!r}")
        return {}
    cleaned = normalize_record(data)
    print("  [hook] normalized:", input_data["tool_name"])
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": rebuild_like(response, json.dumps(cleaned)),
        }
    }


async def main():
    use_hook = True
    if len(sys.argv) > 1 and sys.argv[1] == "raw":
        use_hook = False
    hooks = {}
    if use_hook:
        hooks = {"PostToolUse": [HookMatcher(matcher="mcp__support__.*", 
                                             hooks=[normalize_output])]}
    if use_hook:
        print("=== PostToolUse hook ON ===")
    else:
        print("=== Raw tool output ===")
    options = ClaudeAgentOptions(model=MODEL, 
                                 mcp_servers={"support": SUPPORT_SERVER},
                                 allowed_tools=ALL_SUPPORT_TOOLS, 
                                 hooks=hooks, 
                                 max_budget_usd=1.0)
    async for message in query(prompt=QUESTION, options=options):
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
