# Module 7 Self-Check: Session State, Resumption, and Forking

Four questions in the exam's format. Attempt all four before reading the
answers, and for each one say why the other three fail.

These are original questions written for this course.

## The wrong-answer patterns

Prompt where code belongs. Over-engineered. Different problem. Doesn't exist.
Doubles down. Right verdict, wrong reason.

---

## Question 1

You are three days into a debugging investigation with Claude Code across a
payments service. Each day you stop at a natural point and want to pick up
exactly where you left off, with everything the session has read still in
context. You run other Claude Code sessions in the same directory during the
day for unrelated work. What is the mechanism?

- A. Paste yesterday's final summary into a brand new session at the start of each morning's work
- B. Keep the terminal open and the session running continuously across all three days of work
- C. Name the session, then start each day with --resume and that name to continue where you stopped
- D. Set a session_persist flag in CLAUDE.md so the session is retained automatically between days

## Question 2

After a deep analysis of a codebase, about 40 files and several minutes of
reading, you want to compare two refactoring strategies. Neither should be
influenced by the other's reasoning, and you do not want to pay for the
analysis twice. What do you use?

- A. Fork the session twice, creating two independent branches from the finished analysis for each strategy
- B. Resume the session, try one strategy, then ask it to forget that work and try the other strategy
- C. Run the full analysis twice in two fresh sessions, one for each of the refactoring strategies
- D. Spawn two subagents with the analysis summary written into each of their prompts before they start

## Question 3

You resume a session that analyzed a 40-file codebase last week. Since then a
teammate merged a refactor touching four of those files, including the one
holding the retry logic you were investigating. The resumed agent answers
your first question confidently, citing a function signature that no longer
exists. What should you do?

- A. Tell it to re-read the entire codebase from the top before it answers anything further about it
- B. Tell it which four files changed and what changed in each, so it re-analyzes those and keeps the rest
- C. Do nothing, because a resumed session detects file changes on disk and re-reads them automatically
- D. Set a higher max_tokens so the resumed session has enough room to re-read the code it needs

## Question 4

A teammate resumes a session from a month ago to continue an investigation.
Since then, the service was rewritten: 30 of the 45 files the session read
have changed substantially, and the module structure is different. What is
the more reliable approach?

- A. Resume the old session and trust the agent to notice the differences on its own as it works through
- B. Resume the old session and add "ignore all of your previous analysis" to the very first prompt you send
- C. Fork the old session twice so the stale tool results are isolated inside two separate branches
- D. Start a new session with a structured summary of what still holds, since stale results get reasoned from

---

## Answers

**Question 1: C.** Named session resumption with `--resume` is the exam's
mechanism, and the scenario's detail about other sessions in the same
directory is why the name matters: without it you'd be picking from several.
A works but throws away context the session already has. B is not a strategy.
D invents a setting.

**Question 2: A.** Fork-based session management for divergent approaches
from a shared baseline. B contaminates the second strategy with the first. C
pays twice. D would mostly work, but it compresses the analysis into whatever
you summarized, while a fork carries the full conversation.

**Question 3: B.** Informing the resumed session about specific file changes
gets targeted re-analysis instead of full re-exploration. Four of forty
changed, so the other thirty-six are still good and already paid for. A
throws away the value of resuming. C describes detection that does not
happen, and it's the belief that caused the stale answer. D solves a
truncation problem the scenario never showed.

**Question 4: D.** The exam states it directly: a new session with a
structured summary is more reliable than resuming with stale tool results,
because the stale results stay in context and the agent reasons from them
anyway. Thirty of 45 is most of what it read. A and B leave the stale results
in place, and B adds an instruction the model can't honor, since it can't
un-read a file. C isolates the stale results into two sessions that both
still contain them.
