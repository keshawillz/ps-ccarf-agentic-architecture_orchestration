# Claude Certified Architect - Foundations: Agentic Architecture & Orchestration

![Course title slide](docs/course-title.png)

This is the companion repo for Claude Certified Architect - Foundations: Agentic Architecture & Orchestration on Pluralsight. It covers Domain 1 of the CCAR-F exam, the largest at 27 percent: agentic loops, multi-agent coordination, subagent context passing, programmatic enforcement with hooks, task decomposition, and session resumption and forking.

Each module has demo code you'll watch being built in the course, a hands-on challenge with a broken starter to fix, a worked solution, and a self-check with exam-style questions. Everything runs in GitHub Codespaces with one secret, your `ANTHROPIC_API_KEY`.

## Run it in GitHub Codespaces (recommended)

1. Add your API key as a Codespaces secret named `ANTHROPIC_API_KEY`
   (GitHub → Settings → Codespaces → Secrets), or accept the prompt when the
   Codespace starts.
2. Click **Code → Create codespace on main**.
3. Wait for the container to build. Dependencies install automatically.
4. Open a terminal and run any demo, for example:

   ```bash
   cd module-01-agentic-loops/demo-support-agent-loop
   python agent.py
   ```

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

Python 3.10 or later. The devcontainer uses 3.12.

Modules 2 and up use the Claude Agent SDK, which drives the Claude Code CLI, so
you also need Node.js and:

```bash
npm install -g @anthropic-ai/claude-code
```

Module 1 needs none of that. It runs on the `anthropic` package alone.

## Repo layout

```
module-01-agentic-loops/
  demo-support-agent-loop/       Clips 3 and 4: build and run the agentic loop
  challenge-fix-a-broken-loop/   Clip 6: fix a loop with three real bugs
  self-check.md                  Four exam-style questions to close the module

module-02-multi-agent/         Task 1.2: coordinator-subagent patterns
module-03-subagent-invocation/ Task 1.3: spawning, context passing, parallelism
module-04-enforcement-handoff/ Task 1.4: hooks as gates, multi-issue, handoffs
module-05-hooks/               Task 1.5: PostToolUse normalization, PreToolUse blocks
module-06-task-decomposition/  Task 1.6: prompt chaining vs dynamic decomposition
module-07-sessions/            Task 1.7: resume, fork, start fresh

Each module folder has its own README with the clip map, plus a self-check.md
(except Module 6, whose challenge is already eight scenario judgments).

check_conventions.py            Run before packaging; catches drift across files
```

Module 1 stays on the raw Messages API on purpose, so you see the loop the SDK
runs for you from Module 2 onward. Modules 4 and 5 add hooks to Module 1's
support agent, rebuilt as SDK tools. Modules 6 and 7 work on small codebases
checked into the repo.

## Code style

The Python is deliberately beginner-level: plain loops, explicit if/elif,
no clever idioms. If you're new to Python, nothing in this repo should make
you stop and decode the language. The agent patterns carry the lesson.

## Model and versions

All code pins `claude-sonnet-5`, `anthropic==1.2.0`, and
`claude-agent-sdk==0.2.152`. Sonnet 5 runs adaptive
thinking by default and rejects non-default sampling parameters (`temperature`,
`top_p`, `top_k` return a 400), so the demos set neither.

## Cost note

The demos make a handful of short API calls per run. A full run of every
Module 1 demo and challenge costs a few cents at Sonnet 5 pricing.
