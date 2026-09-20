# Solution Notes

Each fix maps to a named anti-pattern in CCAR-F Task Statement 1.1.

## Fix 1: stop_reason drives the loop

**Anti-pattern removed:** parsing natural language to decide termination,
and treating assistant text as a completion signal.

The kicker in this starter: the system prompt says "reassure the customer
that their issue is being resolved," and the loop scans replies for the
word "resolved". The prompt plants the exact word the exit condition is
hunting for. A single turn can carry that reassuring text alongside a
pending `process_refund` call, and the keyword check fires first. That's
the mid-refund walkaway.

The fix branches on `stop_reason` and nothing else. `"tool_use"` means
Claude is waiting on results. `"end_turn"` means Claude decided it's done.
Any other value raises, because clip 5's remaining stop reasons
(`max_tokens`, `refusal`, `pause_turn`, `stop_sequence`,
`model_context_window_exceeded`) each need deliberate handling, and a loop
that guesses is worse than a loop that stops loudly.

## Fix 2: tool results flow back correctly

**Anti-pattern removed:** breaking the conversation history that Claude
reasons over.

The starter kept only reply text and pasted tool output back as chat
prose. Claude never saw its own `tool_use` blocks, so on the next turn it
had no record of what it called or why. That's where the repeated tool
calls came from.

The fix appends `response.content` untouched, then answers with a user
message containing only `tool_result` blocks, each tied to its call by
`tool_use_id`. Two details matter:

- Thinking blocks ride along inside `response.content`. Passing them back
  untouched is required when thinking and tool use mix.
- The tool-result message carries results only. Extra text beside a
  `tool_result` can end the turn early or error on server tools.

## Fix 3: a retry limit that fails loudly

**Anti-pattern removed:** an iteration cap as the primary stopping
mechanism.

The cap stays, and its job changes. `MAX_TURNS` raises a `RuntimeError`
when tripped, so a runaway loop becomes a visible incident instead of a
silent partial answer. The normal exit is always `end_turn`. If the
tripwire fires often, the move is to investigate the loop or the prompts,
never to quietly raise the number.
