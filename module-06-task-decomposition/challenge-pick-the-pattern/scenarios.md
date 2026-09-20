# Challenge: Pick the Right Pattern Eight Times

For each scenario, pick one: **fixed pipeline** (prompt chaining), **dynamic
decomposition**, or **single call**. Then write the one clue that decided it.

1. A nightly job reviews every merged pull request against the same eight
   criteria and posts a summary.
2. A customer says "something's wrong with my account" and nothing else.
3. Translate a 40-page manual: extract terminology, translate each section,
   check consistency of terms across sections.
4. Investigate why checkout latency doubled last Tuesday.
5. Classify one support ticket into one of six categories.
6. Onboard a new engineer to a codebase nobody has documented.
7. Generate release notes from a list of merged PR titles.
8. Find every place a deprecated payment API is still called and estimate the
   migration effort.

Part two, hands-on. Run `../demo-two-pass-review/two_pass_review.py` against
the review target and read both stages of output. Then answer this:

Find one finding in stage 2 that stage 1 could not have produced, no matter
how carefully it read. Write down which finding it is and why stage 1 was
structurally unable to reach it.

Then the other direction. Look at what stage 1 reported for each file on its
own. Was anything there that stage 2 would have been unlikely to surface?

Answers and reasoning are in `solutions/answers.md`. Commit to yours first.
