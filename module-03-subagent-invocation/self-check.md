# Module 3 Self-Check: Subagent Invocation, Context Passing, and Spawning

Four questions in the exam's format. Attempt all four before reading the
answers, and for each one say why the other three fail.

These are original questions written for this course.

## The wrong-answer patterns

1. **Prompt where code belongs**: prompt guidance when the scenario needs a
   guarantee.
2. **Over-engineered**: new infrastructure when a direct fix exists.
3. **Different problem**: a real fix aimed at a symptom nobody showed.
4. **Doesn't exist**: plausible-sounding features that aren't real.
5. **Doubles down**: more of the broken approach, scaled up.
6. **Right verdict, wrong reason**: the correct conclusion by reasoning that
   doesn't hold.
7. **Blames the wrong agent**: fixing a subagent that was working correctly.

---

## Question 1

Your coordinator is configured with three AgentDefinitions and a system prompt
instructing it to delegate research to them. In three weeks of production it
has never delegated once. It answers every question itself using its own file
tools, the answers are mostly fine, and no exception appears in the logs. A
teammate has already rewritten the descriptions twice with no change. What is
the most likely cause?

- A. The subagent descriptions are too similar, so the coordinator cannot reliably choose between them
- B. The coordinator's system prompt needs stronger wording instructing it to delegate rather than answer
- C. The AgentDefinitions are missing the model field, so the subagents cannot be started when invoked
- D. The coordinator's allowedTools does not include the Task tool, so the invocations are never approved

## Question 2

A coordinator spawns four analysis subagents for four independent files. Each
analysis takes about 20 seconds in isolation, and the total run takes 85
seconds. The coordinator's transcript shows four assistant turns, each
containing exactly one Agent tool call, with each turn waiting for the
previous subagent's result before the next call. What change reduces the
total time?

- A. Raise CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS so more subagents are permitted to run at the same time
- B. Have the coordinator emit all four Agent tool calls together in a single response instead of four
- C. Give each subagent a faster model so every individual analysis finishes in less wall-clock time
- D. Combine the four analyses into one subagent invocation that reads and handles all four files

## Question 3

Your research pipeline passes findings from an analysis subagent to a
synthesis subagent. The synthesis output is well written, but an audit found
citations wrong in a third of reports: source documents attributed to the
wrong claims, and some claims with no citation at all. The analysis subagent's
output is a prose summary of what it found in each document, two or three
paragraphs per source. What is the most effective fix?

- A. Give the synthesis subagent read access to the source documents so it can verify each citation itself
- B. Add an instruction to the synthesis prompt telling it to cite carefully and never misattribute a source
- C. Have the analyst return structured records with source fields per claim, and have synthesis preserve them
- D. Add a validation step after synthesis that checks each citation and retries synthesis when one is wrong

## Question 4

A coordinator runs an expensive codebase analysis, about 40 files and several
minutes of reading, then needs to explore two different refactoring approaches
that both build on that analysis. The two explorations must not influence each
other, and the analysis should not be paid for twice. What is the appropriate
mechanism?

- A. Fork the analysis session twice, so each branch inherits the completed analysis and neither sees the other
- B. Spawn two subagents with the analysis summary written into each of their prompts before they begin
- C. Resume the analysis session twice in sequence, exploring one approach fully and then the other one
- D. Run the analysis twice from scratch, once at the start of each of the two separate explorations

---

## Answers

**Question 1: D.** The exam states it directly in Task 1.3: `allowedTools`
must include `"Task"` for a coordinator to invoke subagents. Leave it out and
the invocations are never approved, so nothing raises and you get a
coordinator that answers everything itself. Note what the scenario tells you:
it answers using its own file tools, so it isn't confused about which subagent
to pick, and the descriptions have already been rewritten twice with no
effect. That rules out A (blames the wrong agent) and shows B is prompt
guidance aimed at something a prompt cannot fix, since no wording makes a tool
available. C describes a requirement that doesn't exist; `model` is optional
and defaults.

Practical note beyond the exam: the tool is named `Task` in the exam guide
and `Agent` in current Claude Code, so production code should list both.

**Question 2: B.** Turns are sequential and everything within a turn can
overlap, so four turns holding one call each means four analyses running one
after another. Putting all four calls in one response is the mechanism, and
the transcript in the scenario is the giveaway. A raises a limit nothing has
hit, since with one call per turn concurrency never exceeds one. C shortens
each analysis without changing the serialization, so it treats a symptom. D
removes the parallelism entirely and hands one subagent four files, which also
invites the attention dilution that per-file passes are meant to avoid.

**Question 3: C.** Prose loses provenance at every handoff, because a
summarizing step keeps the interesting sentence and drops the file name near
it. Structured records fix the root cause by making the source a field
attached to its claim, and both halves are required: the analyst produces the
fields and synthesis is told to preserve them. A changes the architecture so
synthesis does its own research, which reintroduces the work the pipeline
split up and still leaves the handoff lossy. B asks a prompt to guarantee
accuracy over information that was already discarded upstream, and no amount
of care recovers a source that isn't in the input. D builds a retry loop on
top of the broken handoff, and retries can't help when the required
information is absent from what the model received.

**Question 4: A.** Forking is built for exactly this: branch a completed
conversation so each branch inherits everything the baseline learned, and
neither branch sees the other. B is the closest wrong answer and would mostly
work, but it forces you to compress the analysis into a summary and hand over
only what you thought to include, whereas a fork carries the full conversation.
C shares one session between both explorations, so the second exploration sees
the first one's reasoning, which is precisely the influence the scenario
forbids. D pays for the expensive analysis twice, and the cost of that
analysis is the reason the question exists.
