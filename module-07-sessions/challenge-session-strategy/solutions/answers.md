# Answers

## Part one: a resume prompt that passes

```python
RESUME_PROMPT = """Two files changed since you read this code.
- billing/limits.py: SUPERVISOR_THRESHOLD_USD changed from 500.0 to 750.0,
  and a comment was added.
- billing/charges.py: a docstring line was added. No logic changed.
Re-read only those two files. Then tell me which of your earlier conclusions
about process_refund are affected by the new threshold."""
```

The deciding detail is "re-read only those two." Without it, a resumed session
either trusts week-old tool results or re-reads everything, and both cost you.

## Part two

One question runs through A, B, and C: are the prior tool results still valid?

**A. Start fresh with a summary.** Thirty of 45 files changed, so most of what
that session read is now wrong. Briefing will not rescue it, and this is the
part worth understanding. Briefing does not delete anything. Those old file
reads stay in the conversation, and the model reads the whole history every
turn, so it can still draw on them, especially for decisions that are not about
the files you named. At 30 of 45 there is nothing useful left to name. Write a
short summary of what still holds and start clean. The exam's phrasing: a new
session with a structured summary is more reliable than resuming with stale
tool results.

**B. Resume and brief it.** One file changed and you can name it. Say which
file, say what changed, and say to re-read only that. That is targeted
re-analysis rather than full re-exploration. Know what you are getting, though.
It is a compromise on the same axis as A, not a clean fix, and it works here
only because one file out of many went stale.

**C. Resume.** Nothing changed, so every tool result is still true. No briefing
needed.

**D. Fork, and it is not the same kind of choice.** A, B, and C all answer
whether the old context is still good. D answers something else: do you want
one line of work or two? Forking is not a third option beside resume and start
fresh. In the SDK it sits next to resume in the options, so the choice is
append or branch. Leave `fork_session` off and the same call continues the
original.

Two consequences. You still have to make the A/B/C call first, because a fork
has to branch from something. And a fork copies everything in that session,
including anything stale, so forking branches but it does not clean.
