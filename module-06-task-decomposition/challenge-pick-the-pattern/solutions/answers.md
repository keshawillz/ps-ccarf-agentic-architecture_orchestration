# Answers

The clue is always the same question: are the steps known before the run, or
do they come from what the run finds?

1. **Fixed pipeline.** Eight known criteria, same every night. One pass per
   criterion or per file, then a summary pass.
2. **Dynamic decomposition.** Nothing is known until the first lookup. The
   investigation plan comes from the account state.
3. **Fixed pipeline.** Three known stages in a fixed order. Extract, translate
   per section, consistency check across sections. Classic prompt chaining.
4. **Dynamic decomposition.** Open-ended investigation. Each finding decides
   where to look next.
5. **Single call.** One classification with a fixed label set. A pipeline
   adds cost and nothing else.
6. **Dynamic decomposition.** Map structure first, then find what matters,
   then plan. The exam's "add tests to a legacy codebase" scenario, one step
   removed.
7. **Single call.** The input is a list and the output is a summary of it.
   Known shape, no investigation.
8. **Fixed pipeline for the search, dynamic for the estimate.** Finding
   callers is mechanical: grep, then read each hit. Estimating effort depends
   on what those callers turn out to do. Partial credit for either answer if
   the reasoning names the split.

## Part two

**A stage 2 finding stage 1 could not reach.** The strongest example is the
`list_orders` bug: the handler calls `find_order(customer_id)`, and
`find_order` in `order_service.py` looks up by order id, so that endpoint can
never return anything. Stage 1 could not find it at any level of care, because
each pass sees exactly one file. Read `orders_api.py` alone and the call looks
fine, since `find_order` sounds general enough to take a customer id. Read
`order_service.py` alone and the function is correct on its own terms. The bug
lives in the relationship between them, and stage 1 was told not to look at
relationships.

The audit inconsistency is the same kind. `find_order` logs every read while
`lookup_charge` logs none. Each file is self-consistent. Only the comparison
shows the disagreement.

That is the real argument for the two-pass structure, and it does not depend
on a single pass performing badly. It depends on what each pass can see.

**The other direction.** Stage 1's per-file reports include findings stage 2
would likely skip, because stage 2 is asked only for cross-file issues. The
`KeyError` in `issue_refund`, where the function indexes `CHARGES[charge_id]`
directly instead of using `.get()`, is a local bug in one file. So is any
"nothing to report here" verdict, which is worth something: it tells you the
file was actually examined rather than skimmed past.

Neither stage subsumes the other, which is why the pattern is both and not
either.

**One thing worth noticing.** The `ValueError` in `issue_refund`, the
inconsistency the clip points at during the file tour, may not appear in
either stage. A review gives you findings, not a guarantee of completeness.
What the structure gives you is even depth across files and a comparison step
that definitely ran.
