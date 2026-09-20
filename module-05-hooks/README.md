# Module 5: Applying Agent SDK Hooks for Tool-Call Interception and Data Normalization

Maps to CCAR-F **Task Statement 1.5**. The exam guide is the source of truth.

| Clip | Type | Where |
|------|------|-------|
| 1. What hooks are and when they run | Theory | Slides only |
| 2. Demo: Clean up tool data with PostToolUse | Demo | `demo-normalize-data/` |
| 3. Demo: Block refunds over $500 with PreToolUse | Demo | `demo-block-large-refunds/` |
| 4. Decide between a hook and a prompt | Theory | Slides only |
| 5. Challenge: Add both hooks to the support agent | Challenge | `challenge-add-both-hooks/` |

After the challenge, finish with `self-check.md`.

## The two hook shapes

`PreToolUse` runs before a tool call and returns
`hookSpecificOutput.permissionDecision` of `"deny"` with a reason. The call
never executes.

`PostToolUse` runs after the tool returns and before the model reads it, and
returns `hookSpecificOutput.updatedToolOutput` to replace what the model sees.

`normalize.py` has no SDK in it, so the format logic is testable offline.
`messy_tools.py` returns dates three ways and status as an integer, on purpose.
