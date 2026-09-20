# Module 5 Self-Check: Agent SDK Hooks

Four questions in the exam's format. Attempt all four before reading the
answers, and for each one say why the other three fail.

These are original questions written for this course.

## The wrong-answer patterns

Prompt where code belongs. Over-engineered. Different problem. Doesn't exist.
Doubles down. Right verdict, wrong reason.

---

## Question 1

Your support agent calls three backend tools owned by three different teams.
One returns dates as Unix timestamps, one as ISO 8601 strings, one as
US-format text, and order status arrives as an integer code. A review of 200
transcripts found the agent misreading a date or status in 14 percent of
them, usually by treating a Unix timestamp as an order ID. The three owning
teams have declined to change their formats. Where should normalization
happen?

- A. In the system prompt, with a table explaining each date and status format the agent may encounter
- B. In a PostToolUse hook that rewrites each tool result into one format before the model reads it
- C. In each backend service, by changing all three to return dates and statuses in a single format
- D. In a PreToolUse hook that rejects tool calls to any service known to return inconsistent formats

## Question 2

Policy caps agent-issued refunds at 500 dollars; anything higher needs a
supervisor. The system prompt says so. Last month the agent issued two refunds
above the cap, one for 1,200 dollars, and both were discovered a week later by
finance. What is the correct enforcement?

- A. A PostToolUse hook on process_refund that reverses any refund above the cap after it has already posted
- B. A stronger system prompt that repeats the cap in three places and spells out the consequences of a miss
- C. Removing process_refund from the agent's tools entirely and routing every refund request to a human
- D. A PreToolUse hook on process_refund that denies any call above the cap and directs the agent to escalate

## Question 3

A team lead wants every reply to a frustrated customer to open with an
apology before any policy is explained. Reviewing transcripts, the agent does
this about 85 percent of the time. She proposes a PreToolUse hook on
escalate_to_human that denies the call unless the agent's message text
includes the word "sorry," reasoning that rules belong in code. What is the
right call?

- A. Leave it in the system prompt, since tone is a judgment call and a miss costs nothing a hook would prevent
- B. Add the hook as proposed, since anything the team wants enforced consistently belongs in code not prompts
- C. Add a PostToolUse hook that rewrites the agent's reply to insert an apology whenever one is missing from it
- D. Move the apology into the escalate_to_human tool's schema as a required field the agent has to fill in

## Question 4

You add a PostToolUse hook to reformat a tool's output. The hook runs, logging
confirms it fires on every call, and its return value is a dict containing
`hookSpecificOutput` with `hookEventName` set to `PostToolUse` and an
`additionalContext` string describing the cleaned data. Claude still sees the
original, unformatted output. What is the most likely cause?

- A. PostToolUse hooks cannot change tool output at all; only PreToolUse hooks can alter what the model sees
- B. The hook ran after the model had already read the original result, so the replacement came too late
- C. The hook returned additionalContext or nothing rather than updatedToolOutput, so the original output passed through unchanged
- D. The tool's output was cached from a previous run, so the hook never received the new result to modify

---

## Answers

**Question 1: B.** Task 1.5 names this exact case: heterogeneous formats
normalized in a PostToolUse hook before the agent processes them. A asks the
model to do format arithmetic on every turn, which is where the 14 percent
comes from. C is a real fix, and the scenario has already closed it: three
teams declined. Even without that, it's three backend changes across teams
for a problem one hook solves. D blocks the data instead of fixing it.

**Question 2: D.** Intercept the outgoing call, deny above the threshold,
redirect to the alternative workflow. That is the exam's pattern. A lets the
money leave first and then tries to claw it back, which is what finance is
already doing a week late. B doubles down on the approach that already failed.
C removes a tool the agent legitimately needs for the refunds under the cap,
which are most of them.

**Question 3: A.** The exam's rule runs both directions: hooks for
deterministic guarantees, prompts for probabilistic compliance, and the test
is whether a miss costs money or violates policy. A missing apology does
neither. Eighty-five percent on a tone preference is fine, and the remaining
15 percent are judgment calls the prompt should be allowed to make. B applies
the rule without the test, which is over-engineering, and denying an
escalation because a word is missing would block the thing that actually
helps the customer. C and D enforce tone with machinery built for policy,
and D also puts a customer-facing phrase into a schema the human on the other
end has to read.

**Question 4: C.** The hook has to return `updatedToolOutput` to replace what
the model sees. `additionalContext` adds a note alongside the original result
rather than replacing it, and the scenario says that's exactly what the hook
returned. A is false. B misstates the order: PostToolUse runs before the model
reads the result. D invents a caching behavior.
