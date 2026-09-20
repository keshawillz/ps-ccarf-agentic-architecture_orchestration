# Module 2 Self-Check: Coordinator-Subagent Patterns

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
7. **Blames the wrong agent**: fixing a downstream subagent that was working
   correctly. This one is specific to multi-agent questions and it is
   everywhere on this domain.

---

## Question 1

Your coordinator delegates to four subagents for a competitive analysis of a
CRM vendor. The final report covers pricing tiers in depth and never mentions
support quality, integrations, or onboarding, though all three appear in the
source material and the sales team asked about them specifically. The
coordinator's log shows it created three subtasks, all about pricing. Each
subagent returned accurate, well-sourced findings on the subtask it was given,
and none reported an error. What is the most likely root cause?

- A. The synthesis subagent needs instructions to identify coverage gaps in the findings it receives from others
- B. The search subagents' queries were not broad enough and should be expanded to cover more comparison areas
- C. The coordinator's task decomposition was too narrow, so whole areas of the question were never assigned
- D. The subagents' context windows filled during analysis, so their later findings were dropped from the output

## Question 2

A coordinator invokes a synthesis subagent for the second time in a run,
asking it to revise the report after new findings arrive. The revised report is
missing everything from the first pass and covers only the new material. The
coordinator's follow-up prompt reads: "Add these new findings about onboarding
to the report you wrote earlier." Nothing else was included. What explains
the loss?

- A. The second call is a fresh instance with no memory of the first, so the earlier report belongs in the prompt
- B. The subagent's context window was exceeded when the new findings were appended to its existing history from the first call
- C. The coordinator needs to pass a session identifier so the subagent can reload its prior conversation on call
- D. Subagent memory has to be enabled by setting the memory field in the AgentDefinition before the second call

## Question 3

Your research system runs a coordinator with five specialized subagents.
Latency is 40 percent higher than target, and tracing shows most of it is
round trips: the analysis subagent returns to the coordinator whenever it
needs another source, the coordinator calls search, and analysis restarts. A
teammate proposes letting the analysis subagent call the search subagent
directly whenever it needs a source, bypassing the coordinator. What is the
strongest argument against this change?

- A. Subagents are technically incapable of invoking other subagents, so the proposed change cannot be implemented
- B. Direct calls between subagents would exceed the concurrent subagent limit and fail as soon as they are made
- C. The analysis subagent's tool restrictions prevent it from returning search results in a format synthesis accepts
- D. Routing every call through the coordinator preserves observability, consistent error handling, and controlled flow

## Question 4

A coordinator handles both quick factual lookups and deep multi-source
research. Every request runs through the full pipeline: search, then document
analysis, then synthesis, then report generation. Simple lookups such as "what
is vendor X's base price" take 40 seconds and cost four subagent invocations,
and they are 70 percent of traffic. What change best addresses this?

- A. Cache the results of previous lookups so any repeated question can skip the full pipeline entirely
- B. Have the coordinator assess each request's complexity and invoke only the subagents that request needs
- C. Merge the four subagents into one general-purpose agent that handles every request type on its own
- D. Run the four subagents in parallel so the pipeline finishes in the time of the slowest single stage

---

## Answers

**Question 1: C.** The log is the evidence, and it says the coordinator made
three subtasks that were all about pricing. Everything downstream did its job
on the scope it was handed. This is the diagnostic rule for the whole domain:
missing coverage points at the coordinator's split, while a weak answer inside
a covered area points at a subagent's prompt. A, B, and D each blame an agent
that was working correctly, which is the pattern to watch for in multi-agent
questions. B is the most tempting, because broadening search queries sounds
like it would help, but a search subagent asked only about pricing tiers will
faithfully search only for pricing tiers.

**Question 2: A.** Subagents don't inherit the coordinator's conversation, and
they don't share memory between invocations. The second call is a new instance
that receives exactly one thing from the parent: the prompt string. "The
report you wrote earlier" refers to something that, from this instance's
point of view, was never written. The fix is to include the earlier report in
the follow-up prompt. B invents a context-window failure the scenario never
showed, and the symptom would look different anyway, with truncation rather
than clean absence. C and D describe mechanisms that don't work this way:
there is no identifier the coordinator passes to make a subagent reload a
prior conversation as part of normal delegation, and the AgentDefinition
memory field selects a memory source rather than carrying conversation history
between invocations.

**Question 3: D.** Hub-and-spoke keeps every subagent-to-subagent path
running through the coordinator, and the payoff is operational: one place to
watch what happened, one place where errors are handled the same way, and one
place that controls what information reaches whom. Direct calls create paths
nobody is observing. A is factually wrong, since subagents can spawn subagents
and the SDK has a depth limit precisely because they can. B invents a limit
violation the scenario gives no reason to expect. C describes a formatting
problem that isn't the issue and wouldn't be the strongest argument even if
it were.

Worth noting what the right answer is not: it isn't that direct calls never
make sense. A scoped tool for a high-frequency need can be the right call, and
the 40 percent latency is real. What the exam wants here is the reason the
hub exists, so that when you do add a shortcut, you know what you're giving up.

**Question 4: B.** The coordinator's job includes deciding which subagents a
request actually needs, based on its complexity. A factual lookup doesn't need
document analysis and synthesis, and routing it through them anyway is the
cost, multiplied by 70 percent of traffic. A addresses repeat questions only,
and the scenario says nothing about repetition, so the first lookup still
takes 40 seconds. C throws away the specialization and the scoped tool access
that make each subagent reliable, trading a latency problem for a
tool-selection problem. D is the closest wrong answer: parallelism helps when
every step is needed, but these steps are sequential by nature, since
analysis needs the search results and synthesis needs the analysis. Running
them at once isn't possible, and the real fix is not running them at all.
