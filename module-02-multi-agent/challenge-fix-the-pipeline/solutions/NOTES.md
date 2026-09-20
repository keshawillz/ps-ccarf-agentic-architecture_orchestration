# Solution Notes

Every fix is in `COORDINATOR_PROMPT`. The three subagent definitions are
byte-for-byte identical to the starter, which is the lesson: the subagents were
never the problem.

## Fix 1: split the question across all of it

**Exam concept:** overly narrow task decomposition leading to incomplete
topic coverage (Task Statement 1.2).

The starter told the coordinator to find the most prominent area and break that
one into subtopics. Every subtopic then landed inside visual arts, and music,
writing, and film were never assigned to anyone. The subagents returned good
work on the wrong scope.

The fix asks for segments that cover the whole question, and requires the
coordinator to list them before delegating. That second half matters more than
it looks: a decomposition you can't see is a decomposition you can't debug.
Printing SEGMENTS turns the coordinator's most consequential decision into a
line in your logs.

The diagnostic rule worth memorizing: missing coverage points at the
coordinator's split. A weak or wrong answer inside a covered area points at a
subagent's prompt. The exam tests exactly this attribution.

## Fix 2: partition the scope

**Exam concept:** partitioning research scope across subagents to minimize
duplication.

Nothing in the starter told subagents where their territory ended, so each one
searched the whole corpus and two of them analyzed the same files. That costs
tokens and time, and it inflates a finding's apparent support when the same
document arrives twice through different paths.

The fix gives each call one segment and names which segments belong to other
calls. Both halves are needed. Telling a subagent what it owns leaves it free
to wander; telling it what others own draws the boundary.

Note where this lives. Partitioning is not a property of the subagent
definitions. It's written into the prompt the coordinator composes at runtime,
which is why the same three definitions work for both the broken and fixed
versions.

## Fix 3: review and re-delegate

**Exam concept:** iterative refinement loops where the coordinator evaluates
synthesis output for gaps, re-delegates targeted queries, and re-invokes
synthesis until coverage is sufficient.

The starter shipped whatever came out of the first pass. The fix adds a review
step: compare the report against the question, name the gaps, send targeted
follow-ups, ask for a combined report, repeat.

Two details are easy to get wrong. The follow-ups have to carry the existing
findings, because a subagent invoked a second time is a fresh instance with no
memory of the first. And the loop needs a stopping condition based on coverage,
not on a fixed number of passes, which is the same principle as Module 1's
stop_reason: end on the real signal, not on a count.

This is also where the pattern earns the label "agentic." The coordinator
decides how many follow-up rounds the question needs, and that number is not in
your code.
