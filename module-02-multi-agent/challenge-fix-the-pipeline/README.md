# Challenge: Fix the Research Pipeline

You've inherited a research team that keeps producing confident, incomplete
reports. Ask it about the impact of AI on creative industries and you get a
thorough piece about illustrators and galleries. Musicians, writers, and film
crews never come up, even though the corpus has documents on all three.

Your job: fix how the work is split, stop the duplicated effort, and add a
review step that catches gaps before the report ships.

Work in `broken_pipeline.py`. Leave `coverage.py` and the `../sources` folder
alone.

## Step 1: Reproduce the failure

```bash
cd module-02-multi-agent/challenge-fix-the-pipeline
python broken_pipeline.py
```

Watch the delegation log, then read the coverage check at the bottom. Right now
it reports 1 or 2 segments out of 4.

Read the report itself before you change anything. The writing is good. The
attribution is correct. Every subagent did its job well. That's the part worth
sitting with: nothing downstream is broken.

## Step 2 (Task 1): Fix the split

Open `COORDINATOR_PROMPT` and read step 1 of its instructions. It tells the
coordinator to find the most prominent area of the question and break that one
area into subtopics. So the coordinator picks visual arts, splits it into
illustration and galleries, and delegates. Both subagents succeed. The report
covers exactly what was asked for, and the question was asked wrong.

This is the rule to take into the exam: when coverage is missing, look at the
coordinator's split, not at the subagents.

Rewrite that instruction so the coordinator breaks the question into segments
that cover all of it, and have it list the segments before delegating. A line
like "start your response with SEGMENTS:" makes the split visible in the log,
which turns an invisible decision into something you can inspect.

## Step 3 (Task 2): Give each subagent its own slice

Run it again after Task 1. Coverage improves, and you'll likely see two
subagents reading the same files, because nothing tells them where their
territory ends.

Add an instruction that each call gets one segment and is told which segments
belong to other calls. Partitioning lives in the prompt the coordinator writes,
not in the subagent definitions.

## Step 4 (Task 3): Add the review step

Even with a good split, nothing checks the result. Add a step to
`COORDINATOR_PROMPT`:

1. Compare the report against the original question.
2. Name any segment that is missing or thin.
3. Send targeted follow-ups to source-finder and document-analyst for each gap.
4. Ask report-writer for a combined report, and repeat until coverage is
   complete.

The follow-ups have to carry the existing findings with them. A subagent
invoked for the second time is still a fresh instance with no memory of the
first.

## Step 5: Verify

```bash
python broken_pipeline.py
```

You're done when all of these hold:

- [ ] The log shows a SEGMENTS line naming all four segments before any
      delegation.
- [ ] The coverage check reports 4 of 4.
- [ ] No two subagent prompts ask for the same documents.
- [ ] The final report attributes each claim to an outlet and a date.
- [ ] Narrowing your split back to one segment on purpose makes the review step
      catch it and re-delegate. (Undo that after you test it.)

That last check matters most. A gap check that only passes when nothing is
wrong hasn't been tested.

## Notes

Runs cost real money. `max_budget_usd` is set to 3 dollars and the spawn depth
and concurrency caps are in place. Leave them.

Every run varies. The coordinator may split into four segments or six, and it
may batch follow-ups differently. Coverage of 4 of 4 is the bar, not a
particular delegation pattern.

## Stuck?

A worked solution is in `solutions/`, with notes explaining each fix. Try each
task yourself first.
