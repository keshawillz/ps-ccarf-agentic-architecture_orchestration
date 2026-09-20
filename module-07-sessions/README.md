# Module 7: Managing Session State, Resumption, and Forking

Maps to CCAR-F **Task Statement 1.7**. The exam guide is the source of truth.

| Clip | Type | Where |
|------|------|-------|
| 1. Resume, fork, or start over | Theory | Slides only |
| 2. Demo: Pick up yesterday's investigation | Demo | `demo-resume-yesterdays-investigation/` |
| 3. Demo: Fork a session to compare two approaches | Demo | `demo-fork-a-session/` |
| 4. Resume after the code has changed | Theory | Slides only |
| 5. Challenge: Choose the right session strategy | Challenge | `challenge-session-strategy/` |

After the challenge, finish with `self-check.md`.

## Claude Code CLI

You interact with Claude in a terminal, so this module needs the CLI on your PATH. The devcontainer installs the Claude Code CLI. If Claude isn't found, run npm install -g @anthropic-ai/claude-code.

## Two ways to resume

In Claude Code, by name: `claude --resume <session-name>`. From the SDK, save
the `session_id` off the result and pass it back as `resume`.

## Two ways to fork

Module 3 set `fork_session=True` alongside `resume` on a query. This module
uses the standalone `fork_session()` function, which returns a new session id
you then resume. Same result; the function form gives you the id to keep.

## The deciding question

Are the old tool results still true? Yes, resume. Yes and you need branches,
fork. No, start fresh and bring a written summary. Clip 4 and the challenge
are that question applied.

`sample-app/` is a copy of Module 3's billing codebase, so learners already
know it.
