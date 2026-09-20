# Challenge: Fix a Broken Loop

You've inherited a support agent with a bad reputation. Dana was charged
twice for her headphones. The agent verifies her account, finds both
charges, promises a refund, and then exits without refunding anything.

Your job: make `stop_reason` drive the loop, feed tool results back
correctly, and add a retry limit as a safety net.

Work in `broken_agent.py`. The mock backend in `tools.py` is fine as-is,
so leave it alone.

## Step 1: Reproduce the failure

```bash
python broken_agent.py
```

Watch the transcript, then check the last line. The refund ledger prints
after every run. Right now it says EMPTY.

Run it two or three times. You'll see variations, and most runs share the
same ending: the agent says something reassuring about the issue being
resolved and walks away. Sometimes that happens in the same turn where it
tried to call `process_refund`. The refund never runs.

## Step 2 (Task 1): Make stop_reason drive the loop

The broken loop decides Claude is finished by scanning the reply text for
the word "resolved". Claude can produce text and a tool call in the same
turn, so the keyword fires while a refund is still pending. Worse, the
system prompt tells the agent to reassure customers that issues are being
resolved. The prompt plants the exact word the loop is scanning for.

1. Delete the keyword check entirely.
2. Branch on `response.stop_reason` instead:
   - `"tool_use"`: run the requested tools and keep looping.
   - `"end_turn"`: print the final text and return.
   - Anything else: `raise RuntimeError` with the stop_reason in the
     message. Unhandled cases should be loud, never silent.
3. Print the stop_reason at the top of every turn so you can watch the
   loop make its decisions.

## Step 3 (Task 2): Feed tool results back correctly

The broken loop throws away Claude's `tool_use` blocks and pastes tool
output back as plain chat text. Claude loses track of what it called, so
it repeats work and improvises.

1. Append the assistant turn to `messages` exactly as Claude produced it:
   `{"role": "assistant", "content": response.content}`. All of it,
   thinking blocks included.
2. For each `tool_use` block, run the tool and build a `tool_result`
   block: `{"type": "tool_result", "tool_use_id": block.id, "content":
   json.dumps(result)}`.
3. Append one user message whose content is the list of `tool_result`
   blocks and nothing else. No extra text next to tool results.

The `tool_use_id` is the thread that ties a result back to the call that
asked for it. Without it, the API rejects the request.

## Step 4 (Task 3): Add a retry limit as a safety net

The lab guard at the top of the file is a wallet protector, set absurdly
high. Replace it with a real limit that belongs to your loop:

1. Add `MAX_TURNS = 10` and count iterations.
2. When the count exceeds it, `raise RuntimeError` with a clear message.

The limit is a tripwire for runaway behavior. It should fail loudly and
never be the normal way the loop ends. If your agent regularly hits it,
that's a bug report, and quietly exiting would bury it.

## Step 5: Verify

```bash
python broken_agent.py
```

You're done when all of these hold:

- [ ] The transcript shows a stop_reason for every turn, and the run ends
      on `end_turn`.
- [ ] `process_refund` runs on charge CHG-5502 and Claude reports the
      refund_id back to Dana.
- [ ] The final line shows a non-empty refund ledger.
- [ ] The word "resolved" appears nowhere in your control flow.
- [ ] Deleting the `end_turn` branch makes the loop die on your
      `MAX_TURNS` RuntimeError instead of looping forever. (Undo that
      after you test it.)

## Stuck?

A working version with commentary lives in `solutions/`. Try each task on
your own first. The debugging is the lesson.
