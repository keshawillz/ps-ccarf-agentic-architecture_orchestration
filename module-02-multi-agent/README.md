# Module 2: Orchestrating Multi-agent Systems with Coordinator-Subagent Patterns

Maps to CCAR-F Task Statement 1.2.

| Clip | Type | Where |
|------|------|-------|
| 1. How a coordinator works with subagents | Theory | Slides only |
| 2. Why subagents start with a blank slate | Theory | Slides only |
| 3. Demo: Build a research team | Demo | `demo-research-team/` |
| 4. When the coordinator splits the work wrong | Theory | Slides only |
| 5. Demo: Check for gaps and fill them | Demo | `demo-gap-check/` |
| 6. Challenge: Fix the research pipeline | Challenge | `challenge-fix-the-pipeline/` |

After the challenge, finish the module with `self-check.md`.

## The corpus

`sources/` holds eight short documents across four segments of the creative
industries: visual arts, music, writing, and film production. Both demos and
the challenge read from it.

Two documents per segment means a coordinator that splits the question narrowly
produces a report that is confident, well written, and missing half the answer,
which is the failure this module is about.

## Module 1 used the raw API. This module uses the Agent SDK.

You wrote the loop by hand in Module 1 so you could see it. From here the SDK
runs that loop, and your job moves up a level: define the team, then decide
what each member is told.

Extra setup beyond Module 1: the Agent SDK drives the Claude Code CLI, so both
have to be installed. The devcontainer handles it. Locally:

```bash
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
```

## One thing that catches people

A subagent's tools are inherited from the coordinator. The `tools` field on an
AgentDefinition narrows that inherited set; it cannot add to it. If the
coordinator isn't allowed `Read`, no subagent of it can read either, no matter
what its own definition says.

Practical effect: the coordinator's `allowed_tools` has to be the union of
every tool its subagents need, even for tools the coordinator never calls.

## Forks are the exception

Everything above about fresh context applies to a normal subagent. A fork
inherits the parent conversation instead. Module 3 covers forking; nothing in
Module 2 uses it.

## Cost

Every file here sets `max_budget_usd` plus caps on spawn depth and concurrency.
Subagents can spawn subagents, so one question can become a tree of agents.
Leave the caps in place while you work.
