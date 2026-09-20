# Module 3: Configuring Subagent Invocation, Context Passing, and Spawning

Maps to CCAR-F Task Statement 1.3.

| Clip | Type | Where |
|------|------|-------|
| 1. Spawn subagents with the Task tool | Theory | Slides only |
| 2. Define subagents with AgentDefinition | Theory | Slides only |
| 3. Demo: Pass context without losing sources | Demo | `demo-pass-context/` |
| 4. Demo: Run subagents in parallel | Demo | `demo-parallel-subagents/` |
| 5. Write prompts that set goals | Theory | Slides only |
| 6. Challenge: Explore a codebase with parallel subagents | Challenge | `challenge-explore-codebase/` |

After the challenge, finish the module with `self-check.md`.

## Grounding

This module maps to **Task Statement 1.3** of the CCAR-F exam guide. The guide
is the source of truth. Where current SDK behavior differs from it, the guide's
answer is the exam answer and the SDK's behavior is what you write in code.

That happens once here, on the tool name.

## Task or Agent?

The exam calls it the **Task** tool and states that `allowedTools` must include
`"Task"` for a coordinator to invoke subagents. Claude Code renamed it to
**Agent** in v2.1.63. Current releases emit `Agent` in tool_use blocks while
still reporting `Task` in the init tools list, and the docs say to match both.

Every file in this course lists both names:

```python
AGENT_TOOL_NAMES = ["Agent", "Task"]
```

Answer `Task` on the exam. Write both in code.

## What's here

`sources/` holds three policy documents with page markers, used by the clip 3
demo and the parallel demo.

`sample-app/` is a small billing codebase with a refund path and two test
files. The fork demo analyzes it; the challenge explores it.

## Cost

Every file sets `max_budget_usd` plus caps on spawn depth and concurrency.
The parallel demo runs several subagents at once by design, so the concurrency
cap matters more here than in Module 2.
