"""Demo: Check for gaps and fill them.

The team produced a report. Nobody checked whether it answered the
whole question. This demo adds that step.

The draft below is a real first-pass result: three subagents ran, each did its
job correctly, and the report still only covers visual arts. The coordinator's
new job is to audit the draft against the question, name what is missing, send
targeted follow-ups, and rebuild.

The draft is written into this file on purpose. We've already seen the full
pipeline running, so this clip spends its time on the review loop instead of
re-running work you have seen.

Run it:
    python gap_check.py
"""

import asyncio

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

MODEL = "claude-sonnet-5"
SOURCES_PATH = "../sources"
AGENT_TOOL_NAMES = ["Agent", "Task"]

# The coordinator's allowed_tools has to include every tool its subagents
# use, even ones the coordinator never calls itself. allowed_tools is a
# permission allowlist, and in a non-interactive run a subagent's call to an
# unlisted tool is denied rather than prompted. Tested on this SDK version;
# how subagents inherit tools and permissions has open bugs, so re-verify
# after upgrading.
SUBAGENT_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + SUBAGENT_TOOLS

QUESTION = "What is the impact of AI on creative industries?"

DRAFT_REPORT = """AI's impact on creative industries falls hardest on routine
production work.

Commercial illustration: a survey of 412 illustrators found 61 percent lost at
least one recurring client to in-house generative tooling since 2024, while 44
percent raised rates on the work they kept. (Studio Practice Review, 2026-02-11)

Galleries: of 30 major galleries reviewed, 11 require disclosure of generative
tools, 6 prohibit generative work, and 13 have no written policy.
(Contemporary Curation Quarterly, 2026-04-02)

Overall, the picture is one of routine work disappearing while senior judgment
becomes more valuable."""

COORDINATOR_PROMPT = """You are the coordinator of a research team, and this
run is a review pass.

You will be given a research question and a draft report produced by an earlier
pass. Your job:

1. Audit the draft against the question. List every segment of the question
   the draft does not cover. Be specific. "Creative industries" is broader than
   any one segment, so name the ones that are missing.
2. For each gap, send a targeted follow-up to source-finder, then to
   document-analyst. Give each call one gap to work on and say which gaps
   belong to other calls, so no two subagents cover the same ground.
3. Send the draft plus all the new findings to report-writer and ask for one
   combined report.

Subagents remember nothing between calls and cannot see this conversation.
Every fact a subagent needs has to be written into the prompt you send it,
including the draft's existing content when the report-writer needs it.

Start your response with a line beginning "GAPS FOUND:" listing the missing
segments, so the gaps are visible before any delegation happens."""

SOURCE_FINDER = AgentDefinition(
    description=(
        "Finds which source documents are relevant to a given slice of a "
        "research question. Returns file names and a one-line reason for each."
    ),
    prompt=f"""You locate relevant documents. The corpus is in {SOURCES_PATH}.

Use Glob to list the files and Grep to search their contents. Each file starts
with a metadata block containing title, outlet, published date, url, and domain.

You will be given one gap to work on. Return only the files relevant to that
gap, with the file name, the domain field, and one line on why it is relevant.
Do not summarize the documents.""",
    tools=["Glob", "Grep", "Read"],
    model=MODEL,
)

DOCUMENT_ANALYST = AgentDefinition(
    description=(
        "Reads specific source documents and extracts findings with "
        "attribution. Use after source-finder has identified the files."
    ),
    prompt="""You read source documents and pull out findings.

You will be given file names and the gap you are responsible for. Read those
files only. Return findings in this format:

  FINDING: one sentence stating what was found
  EVIDENCE: a short quoted phrase or a number from the document
  SOURCE: the file name
  OUTLET: the outlet field from the metadata block
  PUBLISHED: the published date from the metadata block

Every finding carries its source. No exceptions.""",
    tools=["Read", "Grep"],
    model=MODEL,
)

REPORT_WRITER = AgentDefinition(
    description=(
        "Combines a draft report and new findings into one final report. "
        "Needs everything supplied in its prompt; it has no file access."
    ),
    prompt="""You write the final report.

You will be given a draft report and a set of new findings. Merge them into one
report that keeps the draft's existing content and adds the new material.

Structure:
  - A short opening that answers the research question directly
  - One section per industry segment
  - A Coverage section naming anything still not addressed

Keep every claim attached to the outlet and date it came from. You have no file
access, so do not add facts that are not in what you were given.""",
    tools=[],
    model=MODEL,
)


async def run_review():
    prompt = (
        f"Research question: {QUESTION}\n\n"
        f"Draft report from the first pass:\n\n{DRAFT_REPORT}\n\n"
        "Audit this draft, fill the gaps, and return one combined report."
    )

    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=COORDINATOR_PROMPT,
        allowed_tools=COORDINATOR_TOOLS,
        agents={
            "source-finder": SOURCE_FINDER,
            "document-analyst": DOCUMENT_ANALYST,
            "report-writer": REPORT_WRITER,
        },
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=2.0,
    )

    final_report = ""
    async for message in query(prompt=prompt, options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  -> follow-up sent to: {which}")

        if hasattr(message, "result"):
            final_report = message.result

    return final_report


async def main():
    print(f"Research question: {QUESTION}")
    print("\nDraft report covers: visual arts only")
    print("\nReview pass:")
    report = await run_review()
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
