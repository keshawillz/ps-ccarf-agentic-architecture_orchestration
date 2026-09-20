"""Demo: Plan tests for a legacy codebase.

"Add comprehensive tests" has no fixed step list. The right plan depends on
what the code turns out to contain, so the plan has to be built from
discoveries: map the structure first, find the high-impact areas, then
prioritize, and let the plan change as dependencies surface.

That is the exam's dynamic adaptive decomposition. Contrast with where
the steps were known before the run started.

Run it:
    python adaptive_plan.py
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

MODEL = "claude-sonnet-5"
TARGET = "../review-target"

PROMPT = f"""You are planning tests for the legacy code under {TARGET}, which has none.

Do this in stages, and let each stage change the next:

1. MAP: list every module and what it does, and which modules call which.
   Print a section headed MAP.
2. IMPACT: from the map, pick the areas where a bug would cost the most,
   with one line each on why. Money movement and anything every path depends
   on rank high. Print a section headed IMPACT.
3. PLAN: a prioritized test plan for those areas. For each item, name the
   function, the behavior to pin down, and any dependency you would have to
   fake. Print a section headed PLAN.
4. REVISE: while writing the plan, if you discovered a dependency that
   changes the priority or adds a case, say so in a section headed REVISED,
   and update the plan. If nothing changed, say so.

The plan is the deliverable. Do not write test code."""


async def main():
    options = ClaudeAgentOptions(model=MODEL, allowed_tools=["Read", "Glob", "Grep"],
                                 max_budget_usd=1.5)
    async for message in query(prompt=PROMPT, options=options):
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
