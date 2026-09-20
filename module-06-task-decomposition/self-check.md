# Module 6 Self-Check: Task-Decomposition Strategies

Four questions in the exam's format. Attempt all four before reading the
answers, and for each one say why the other three fail.

Clip 5 already had you judge eight scenarios on which pattern fits. These go
after the parts that exercise doesn't reach: why a review splits the way it
does, when chaining is the wrong call, how open-ended work gets planned, and
the case where the right answer is no decomposition at all.

These are original questions written for this course.

## The wrong-answer patterns

Prompt where code belongs. Over-engineered. Different problem. Doesn't exist.
Doubles down. Right verdict, wrong reason.

---

## Question 1

Your automated reviewer analyzes each pull request in a single pass, reading
every changed file together. On a 14-file PR touching the payments module, the
output flags a missing null check in `refund_handler.py` as a critical issue,
and says nothing about the identical missing check in `credit_handler.py` in
the same PR. It also gives four paragraphs of detail on the first two files
and one line each on the last six. The review criteria are specific and were
identical for every file. What restructuring addresses this?

- A. Require developers to break any pull request over five files into smaller separate submissions before review
- B. Run three independent single-pass reviews and report only findings that appear in at least two of them
- C. Move to a model with a larger context window so all fourteen files fit inside one pass comfortably
- D. Review each file alone for local issues, then run one pass over all files for cross-file consistency

## Question 2

A team automates their release process with a fixed four-stage chain: collect
merged PR titles, group them by type, draft the release notes, then check the
draft against the style guide. It has run nightly for six months without
incident. This week they want to add a stage that investigates why the build
time regressed over the last release, and they plan to add it as stage five in
the same chain. What is the problem with that plan?

- A. The investigation has no knowable steps, so the plan has to come from what each finding turns up
- B. Chaining five stages passes the practical limit, and pipelines that long should be broken into separate workflows
- C. The new stage belongs before the other four, since the drafting stage will need to reference build-time data
- D. Build-time regression is a performance concern rather than a release concern, so another team's automation should own it

## Question 3

You inherit a 200-file service with no tests and are asked to add meaningful
coverage. You have two weeks. Nobody on the current team wrote the original
code, there is no documentation, and the only thing known is that it handles
payment settlement for about 40,000 transactions a day. Which approach fits
the work?

- A. Write one test per public function across all two hundred files, working alphabetically so progress stays measurable
- B. Have the model generate a full test suite in one pass, then spend two weeks correcting its output
- C. Map the call paths, decide where a bug costs most, then build a plan and revise it
- D. Start with the files that changed most often in version control, since churn correlates well with defect density

## Question 4

A support tool receives one customer message at a time and must assign it to
one of six categories: billing, shipping, returns, technical, account, or
other. The categories are fixed, the messages average three sentences, and
accuracy on a labeled sample is already 96 percent with a single API call and
a short prompt. A teammate proposes restructuring it as a chain: extract the
key entities, classify against each category in turn, then reconcile the
results. How should you evaluate that proposal?

- A. Adopt it, because checking each category separately lowers the chance that two similar categories get confused
- B. Decline it, because one input and one output needs no pipeline, and a chain only adds cost
- C. Adopt it only for messages the current approach scores as low confidence, leaving other messages on one call
- D. Decline it, because six categories pass what a chain handles reliably and reconciliation becomes the accuracy bottleneck

---

## Answers

**Question 1: D.** Two symptoms, one cause. The contradictory finding and the
uneven depth both come from asking one pass to hold fourteen files at once,
which the exam calls attention dilution. The fix is the exam's own: per-file
local analysis plus a separate cross-file integration pass. Per-file gives
every file the same depth, and the integration pass is the only step ever
asked to compare files, which is what catches the identical gap in
`credit_handler.py`. A shifts the work to developers and changes nothing about
the system, and five files would still dilute across five files. B suppresses
real findings, since anything caught by one run out of three gets dropped by
the consensus rule. C confuses capacity with attention; the files already fit,
and fitting was never the problem.

**Question 2: A.** The existing four stages qualify for chaining because their
steps were known before the first run, and six months of clean nightly runs
confirms it. "Why did the build time regress" has no such steps. What you find
first determines where you look next, which is dynamic decomposition, and it
does not belong bolted onto a fixed chain. B invents a stage limit that does
not exist. C reorders stages to solve a dependency the scenario never
describes, since the release notes do not reference build time. D reassigns
the work instead of answering how to structure it, and the question is about
decomposition, not ownership.

**Question 3: C.** The exam's sequence for open-ended work, almost exactly:
map the structure, identify the high-impact areas, then build a prioritized
plan that adapts as dependencies surface. The scenario supplies the reason it
has to work this way, since nobody knows the code and two weeks will not cover
two hundred files. A treats every file as equal, and alphabetical order
guarantees the two weeks go somewhere arbitrary. B skips the judgment entirely
and leaves you reviewing output you have no basis to evaluate. D is the
closest wrong answer and the most tempting, because churn genuinely does
correlate with defects. It is a ranking heuristic, not a plan, and it cannot
tell you that settlement is where a bug costs the most.

**Question 4: B.** One input, one output, no steps in between, and 96 percent
accuracy already. Decomposition costs tokens and latency and buys nothing,
which is the wrong answer the exam plants when the simplest approach was right
all along. A asserts a benefit with nothing behind it, and classifying six
times instead of once is more opportunity for confusion, not less. C reaches
the right instinct about not restructuring everything, and it still builds and
maintains a pipeline for a problem the scenario never shows, with no
confidence threshold mentioned anywhere. D lands on decline for an invented
reason: chains have no six-category limit, and the reconciliation bottleneck
is a claim with no support. Right verdict, wrong reason, and on this exam that
is still wrong.
