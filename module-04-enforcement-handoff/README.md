# Module 4: Implementing Multi-step Workflows with Enforcement and Handoff Patterns

Maps to CCAR-F **Task Statement 1.4**. The exam guide is the source of truth.

| Clip | Type | Where |
|------|------|-------|
| 1. Why prompts can't enforce the rules | Theory | Slides only |
| 2. Demo: Block a refund until the customer is verified | Demo | `demo-verify-gate/` |
| 3. Handle requests with more than one problem | Theory | Slides only |
| 4. What a good escalation handoff includes | Theory | Slides only |
| 5. Demo: Escalate with a useful handoff | Demo | `demo-handoff/` |
| 6. Challenge: Lock down the refund workflow | Challenge | `challenge-lock-down-refunds/` |

After the challenge, finish with `self-check.md`.

## The support agent, on the SDK

`support_tools.py` is Module 1's Harbor Audio backend rebuilt as Agent SDK
tools with `@tool` and `create_sdk_mcp_server`. Tool names on the wire are
`mcp__support__<name>`; that is the string `allowed_tools` and hook matchers
use. Each demo folder carries its own copy so it runs standalone.

## How the gate works

The exam's example is blocking `process_refund` until `get_customer` has
returned a verified customer ID. Two hooks do it: a `PostToolUse` hook on
`get_customer` records verified IDs, and a `PreToolUse` hook on `lookup_order`
and `process_refund` returns `permissionDecision: "deny"` until one exists.
A denied call never runs, regardless of what the model was told.

Run every demo with and without its hook. The difference is the module.
