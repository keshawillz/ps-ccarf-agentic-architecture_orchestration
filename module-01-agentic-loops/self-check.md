# Module 1 Self-Check: Agentic Loops

Four questions in the exam's format: a production scenario, one correct
answer, three distractors built to catch partial knowledge. Attempt all four
before reading the answers, and for each one say why the other three fail.
That second habit is worth more points than the first.

These are original questions written for this course.

## The wrong-answer patterns

The exam reuses a small set of distractor patterns. Learn to name them and
you can rule out wrong answers faster:

1. **Prompt where code belongs**: prompt guidance offered when the scenario
   demands a guarantee. Prompts are probabilistic; hooks and gates are not.
2. **Over-engineered**: classifiers, routers, or new infrastructure when a
   direct fix exists.
3. **Different problem**: a real fix aimed at a symptom the scenario never
   showed.
4. **Doesn't exist**: flags, settings, or behaviors that sound plausible and
   aren't real.
5. **Doubles down**: more of the broken approach, scaled up.
6. **Right verdict, wrong reason**: reaches the correct conclusion by
   reasoning that doesn't hold.

---

## Question 1

Your expense-report agent calls `extract_line_items` on a receipt, gets a
clean result, then calls the same tool again on the next turn with identical
input, and sometimes a third time. Logs show the loop stores only the text of
Claude's reply as the assistant turn, dropping the `tool_use` blocks, and
pastes each tool's output back into the conversation as a plain chat message.
Token spend per receipt has tripled. What fixes the repeated calls?

- A. Move each tool's output into the system prompt so the model can see it on every remaining turn
- B. Append the assistant message exactly as returned, then answer it with tool_result blocks matched by tool_use_id
- C. Add a system prompt rule telling the model never to repeat a tool call it has already completed
- D. Set tool_choice to "any" so the model must select a different tool on each successive loop iteration

## Question 2

Four teams describe their systems. Which one exhibits model-driven
decision-making as the exam defines it?

- A. Code matches the request against regex patterns, runs the mapped tool chain, and Claude drafts the reply
- B. Claude is called once per stage of a fixed pipeline, first to extract, then to classify, then to draft
- C. A configuration file lists the tool order for each request type, and Claude fills in each tool's arguments
- D. After each tool result is appended, Claude reads the conversation and emits the next tool_use block itself

## Question 3

A nightly maintenance agent runs its loop as `for i in range(8)`, added a year
ago "to keep costs bounded," and returns whatever the last response was.
Reviewing last month's output, you find that complex jobs shipped
half-finished on eleven nights, and nothing in the logs marked any of them as
a failure. The on-call engineer only noticed because a downstream report was
missing sections. How should the loop be restructured?

- A. Loop on stop_reason, with a MAX_TURNS tripwire that raises so overruns surface as failures instead of output
- B. Raise the range to 20 iterations so complex jobs have enough room to finish before the loop ends
- C. Instruct the model to write INCOMPLETE in its reply when work remains, then check the reply for that string
- D. Lower max_tokens so each turn costs less and more iterations fit inside the same overall token budget

## Question 4

A support agent must verify a customer before it looks up an order. A
teammate proposes this design: call Claude once to classify the request type,
run the tool sequence mapped to that type from a lookup table, then call Claude
once more to write the reply. They describe it as an agentic loop because it
makes three API calls and uses tools. How should the system be characterized?

- A. Model-driven, because Claude is called multiple times and its classification determines which tools run
- B. Pre-configured, because it uses a lookup table instead of reading stop_reason to decide when to terminate
- C. Pre-configured, because the tool sequence is fixed at design time and Claude never chooses the next action
- D. Model-driven, because tool results are returned to Claude before the final reply is written and sent

---

## Answers

**Question 1: B.** The conversation history is missing half the exchange.
With its own `tool_use` turn dropped, the model has no record that it asked
for anything, so from its point of view the first call never happened. The
fix is the pair of appends from clip 2: the assistant turn goes back
untouched, and the results ride in `tool_result` blocks matched by
`tool_use_id`. A misreads what the system prompt is for; it sets behavior
rather than storing data, and the history still claims no call was made
(different problem). C asks the prompt to patch what the history broke, and
the model can't honor "don't repeat yourself" when the record shows nothing to
repeat (prompt where code belongs). D changes tool selection pressure, not
memory; `"any"` forces some tool call every turn and can make the repetition
worse (different problem).

**Question 2: D.** Model-driven means Claude selects the next action by
reasoning over the conversation, and the code's job is to execute whatever it
requests. A and C are pre-configured: in A the regex owns tool selection, and
in C the config file does, with Claude reduced to filling in arguments.
Picking arguments is not picking actions. B is a workflow, and a fine one,
but its steps were fixed at design time. On the exam, "reasons about which
tool to call next based on context" marks the model-driven pattern; any fixed
sequence, however many API calls it makes, is pre-configured.

**Question 3: A.** Two changes, and the exam expects both: `stop_reason`
becomes the exit condition, and the cap changes jobs from stop signal to
tripwire. Raising is the point, because a runaway loop should become a visible
incident rather than a quiet partial answer, which is exactly what the eleven
silent nights were. B keeps the cap as the stop signal and moves the cliff;
complex jobs will find it (doubles down). C swaps one text-scanning
termination hack for another, and the model reliably writing INCOMPLETE is the
kind of promise prompts can't keep (prompt where code belongs). D optimizes
cost per turn, which was never the symptom, and adds truncation as a second
bug (different problem).

**Question 4: C.** The deciding question is who picks the next action, and
here it's the lookup table. Claude classifies, and your code maps that
classification to a sequence someone wrote in advance, so no tool choice is
ever made from what a previous result contained. A is the trap the question
is built around: multiple API calls are not evidence of anything, and a
five-step chain makes five calls without being an agent. D describes returning
tool results to Claude, which a model-driven loop needs but which a fixed
pipeline can also do while never letting Claude choose. B reaches the right
verdict for the wrong reason: what makes it pre-configured is the fixed
sequence, not the absence of a `stop_reason` check. When two options share a
verdict and differ only in why, the reasoning is the question.
