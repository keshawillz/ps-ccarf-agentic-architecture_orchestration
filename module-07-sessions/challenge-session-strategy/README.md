# Challenge: Choose the Right Session Strategy

Part one is hands-on. Part two is judgment.

## Part one

1. Run `../demo-resume-yesterdays-investigation/resume_investigation.py start` to create a session
   that has read the refund code.
2. Change two files. Add a comment line to `billing/limits.py` and change
   `SUPERVISOR_THRESHOLD_USD` to `750.0`. Add a docstring line to
   `billing/charges.py`.
3. Resume the session with a prompt that names exactly those two files and
   says what changed. Ask which of its earlier conclusions are affected.
   Watch whether it re-reads only those two files or everything.
4. Fork the resumed session twice and ask each fork for a different
   refactoring of `partial_refund`. Confirm neither mentions the other.

Write your resume prompt into `strategy.py` where the placeholder is, then
run it. The script checks that your prompt names both changed files.

Do step 2 before step 3. If you resume and claim files changed when they haven't, the session re-reads them, finds nothing different, and you learn nothing about targeted re-analysis.

## Part two

For A, B, and C, say **resume**, **resume and brief it**, or **start fresh
with a summary**, and give the one fact that decided it. Then answer D, which
is asking something different.

A. You analyzed a codebase last week. Since then a teammate merged a
   refactor touching 30 of its 45 files.
B. You analyzed a codebase yesterday. This morning one config file changed,
   and you know which one and what changed in it.
C. You paused a debugging session mid-investigation to go to a meeting.
   Nothing changed while you were gone.

Then one more, and it is a different question:

D. You finished a deep root-cause analysis an hour ago and want to try two
   different fixes without either one influencing the other. What do you do,
   and why is this not the same kind of choice as A, B, and C?

Answers in `solutions/answers.md`. Commit to yours first.
