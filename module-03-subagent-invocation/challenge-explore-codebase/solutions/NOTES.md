# Solution Notes

## Fix 1: two subagents, scoped tools

**Exam concepts:** AgentDefinition configuration including descriptions,
system prompts, and tool restrictions per subagent type; restricting each
subagent's tool set to those relevant to its role.

The starter's single `explorer` failed twice over. Its description gave the
coordinator nothing to route on, and its tool list included `Write`, `Edit`,
and `Bash` for a job that only ever reads.

The two replacements each say when to use them and when not to. `test-finder`
ends with "Does not trace application logic," and `refund-tracer` ends with
"Does not inventory test files." That second half is what the exam is after
when it talks about descriptions that differentiate similar tools. A
description that only says what a subagent does leaves the coordinator to
guess at the boundary.

Both are read-only. The exam's framing is that agents with tools outside their
specialization tend to misuse them, and the cheapest way to prevent misuse is
not handing over the tool.

## Fix 2: one response, two Agent calls

**Exam concept:** spawning parallel subagents by emitting multiple Task tool
calls in a single coordinator response rather than across separate turns.

This is the whole mechanism, and it's easy to state and easy to miss. Turns are
sequential. Everything inside one turn can overlap. So parallelism is not a
setting you switch on, it's a consequence of where the calls land.

The starter said "wait for it to finish," which forced the split across turns.
The fix says to emit both calls in the same response and not to wait.

Two things worth knowing beyond the exam. Since Claude Code v2.1.198 subagents
run in the background by default, and the `background` field on AgentDefinition
can force it per agent. And concurrency is capped, which is why every file in
this course sets `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` rather than trusting
the default.

## Fix 3: a PATH field on every finding

**Exam concept:** using structured data formats to separate content from
metadata when passing context between agents, to preserve attribution.

The starter asked for a description of what was found. Descriptions are prose,
and prose loses provenance at every handoff, because a summarizing step keeps
the interesting sentence and drops the file name attached to it.

The fix asks for blocks with named fields, and states that PATH is required.
The coordinator is then told to keep PATH values exactly as reported. Both
halves matter: producing the metadata is useless if the next step reformats it
away.

The same principle drives clip 3's demo, where the field is a page number
rather than a file path. Content and metadata as separate labeled fields, all
the way through the pipeline.
