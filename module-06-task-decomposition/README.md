# Module 6: Designing Task-Decomposition Strategies for Complex Workflows

Maps to CCAR-F **Task Statement 1.6**. The exam guide is the source of truth.

| Clip | Type | Where |
|------|------|-------|
| 1. Two ways to break up a big job | Theory | Slides only |
| 2. Demo: Fix a code review that contradicts itself | Demo | `demo-fix-contradicting-review/` |
| 3. Demo: Plan tests for a legacy codebase | Demo | `demo-plan-legacy-tests/` |
| 4. Read the signals: which pattern | Theory | Slides only |
| 5. Challenge: Pick the right pattern eight times | Challenge | `challenge-pick-the-pattern/` |

This module has no bookend question and no self-check by design: clip 5 is
already eight scenario judgments.

## The review target

`review-target/` is a five-file pull request with planted cross-file
inconsistencies: two handlers skip validation their siblings perform,
`issue_refund` raises where every other error path returns a status dict, and
`find_order` writes to the audit log for a read. A single-pass review tends to
flag one and approve its twin.

## The exam's two patterns

Fixed sequential pipeline, which the exam calls prompt chaining: steps known
before the run. Clip 2's per-file passes plus a cross-file pass.

Dynamic adaptive decomposition: steps come from what the run discovers. Clip
3's map, then impact, then plan, then revise.

Note for learners searching the docs: Claude Code has a feature named
"dynamic workflows" that is not this. It moves the plan into a script the
runtime executes, which is closer to a fixed pipeline. The exam's term is the
one to learn.
