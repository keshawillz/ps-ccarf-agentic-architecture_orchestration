# Module 4 Self-Check: Enforcement and Handoff Patterns

Four original questions in the exam's format. Attempt all four, then for each
say why the other three fail. Distractor shapes: prompt where code belongs,
over-engineered, different problem, doesn't exist, doubles down, right verdict
wrong reason.

## Question 1

Logs show that in 8 percent of runs your support agent calls lookup_order
using a customer ID the customer typed, without ever calling get_customer.
Two refunds went to the wrong account. What most effectively fixes this?

- A. A PreToolUse hook that denies lookup_order and process_refund until
  get_customer has returned a verified customer ID
- B. A system prompt line stating that get_customer is mandatory before any
  order operation
- C. Few-shot examples showing the agent calling get_customer first even when
  the customer supplies an ID
- D. A routing classifier that enables only the tools appropriate to each
  request type

## Question 2

A customer's message raises three separate issues: a damaged item, a duplicate
charge, and a loyalty question. The agent replies about the duplicate charge
and nothing else, and the customer writes back twice more. What is the
appropriate pattern?

- A. Decompose the message into issues, investigate each with shared customer context, then send one combined reply
- B. Spawn one subagent per issue with no shared context, then concatenate their three replies into one
- C. Ask the customer to submit one issue at a time so each one gets the agent's full attention
- D. Increase max_tokens so the agent has enough room in one reply to address all three issues

## Question 3

Your agent escalates a refund dispute to a human. The human receives "customer
is frustrated about a refund" and nothing else, and has no access to the
transcript. What should the handoff contain?

- A. The customer ID, the root cause as understood so far, the amounts involved, and a recommended action
- B. The full conversation transcript, attached to the ticket so the human can read every turn
- C. A sentiment score for the customer along with the complete text of their most recent message
- D. The list of tools the agent called, in order, with each tool's input and result attached

## Question 4

A teammate argues that the verification rule is already in the system prompt
and the agent follows it in 92 percent of runs, so a hook is redundant. What
is the strongest response?

- A. Prompt instructions have a non-zero failure rate, and financial operations require deterministic compliance from code
- B. Hooks execute faster than prompt instructions, so the agent will respond more quickly on every turn
- C. The prompt should be rewritten with stronger language until compliance measures at a full 100 percent
- D. A hook is redundant because the SDK already enforces tool ordering by default on every single run

---

## Answers

**Q1: A.** Task 1.4's own example, almost word for word: block downstream tool
calls until the prerequisite has completed. B and C are prompt where code
belongs; the scenario already shows prompt compliance failing with financial
consequences. D addresses which tools exist, not the order they run in, which
is a different problem.

**Q2: A.** Decompose, investigate each in parallel using shared context,
synthesize one resolution. B loses the shared context, so each subagent
re-verifies or fails to. C moves the work to the customer. D solves a
truncation problem the scenario never showed.

**Q3: A.** The exam lists exactly these fields, and the reason is the last
sentence of the scenario: the human cannot see the conversation. B is a
transcript dump, which is what the structured summary exists to replace. C
and D describe the agent's process, not the customer's situation.

**Q4: A.** This is the distinction Task 1.4 is built on. Ninety-two percent
is a failure rate of eight percent, and when the failure is a refund to the
wrong account, probabilistic compliance is not compliance. B invents a speed
benefit. C doubles down on the approach that is already failing. D describes
a default that does not exist.
