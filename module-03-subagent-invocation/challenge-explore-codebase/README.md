# Challenge: Explore a Codebase with Parallel Subagents

You've been handed an unfamiliar codebase in `../sample-app` and two questions:
where are the tests, and how does the refund path work?

The starter answers both, slowly, with findings nobody can verify. Your job is
to split the work across two specialized subagents, run them at the same time,
and make every finding traceable to a file.

Work in `explore.py`. Leave `findings_check.py` and `../sample-app` alone.

## Step 1: Reproduce the problem

```bash
cd module-03-subagent-invocation/challenge-explore-codebase
python explore.py
```

Watch the spawn log, then read the two checks at the bottom. You'll see the
second spawn land well after the first, and a report that mentions maybe two
of the five files by name.

Read the report before changing anything. It sounds informed. Now try to act
on it: pick any claim and find the line of code it refers to. Without paths,
you can't.

## Step 2 (Task 1): Two subagents, scoped tools

One `explorer` currently does both jobs with `Glob`, `Grep`, `Read`, `Write`,
`Edit`, and `Bash`. Two problems with that.

The description says it "looks at code and answers questions about it," which
gives the coordinator no basis for choosing it for one job over another. When
a coordinator has one generic subagent, it never has to decide anything, and
you lose the routing that makes the pattern worth using.

And this is a read-only investigation that can write files and run shell
commands. Nothing here needs that.

Replace `EXPLORER` with two definitions:

- `test-finder`, for inventorying test files
- `refund-tracer`, for following `process_refund` through its call chain

Give each a description that says when to use it *and* when not to, and give
both only `Glob`, `Grep`, and `Read`.

Remember from Module 2 that a subagent's tools are inherited from the parent
and narrowed by its `tools` field. The coordinator's `allowed_tools` still has
to include everything the subagents need.

## Step 3 (Task 2): Spawn them in one response

The coordinator prompt currently says to ask for the tests, wait, then ask for
the refund trace. That's two turns, so the second investigation can't start
until the first finishes, and the two questions have nothing to do with each
other.

Rewrite the prompt to spawn both in a single response. Say it plainly: emit
both Agent tool calls in the same response, do not wait for one to return
before starting the other.

The spawn log is how you check. Two spawns within a second of each other went
out together.

## Step 4 (Task 3): Require a path on every finding

Both subagent prompts should specify an output format with a `PATH` field, and
should say that the field is required. Ask for structured blocks rather than
prose, so the path travels attached to the claim instead of somewhere near it.

Then tell the coordinator to keep the `PATH` values exactly as reported. This
is the Module 3 lesson in one line: metadata survives a handoff only when it's
a labeled field, not a sentence.

## Step 5: Verify

```bash
python explore.py
```

You're done when all of these hold:

- [ ] The spawn log shows two spawns within about a second of each other.
- [ ] The path check reports 5 of 5.
- [ ] Each subagent has a description that says when to use it and when not to.
- [ ] Neither subagent can write, edit, or run shell commands.
- [ ] Every finding in the report carries a file path.

## Notes

`max_budget_usd` is set to 3 dollars, with spawn depth and concurrency caps.
Leave them in place.

Runs vary. The subagents may report files in a different order or find extra
detail. The two checks are the bar, not a particular report.

## Stuck?

A worked solution is in `solutions/`. Try each task yourself first.
