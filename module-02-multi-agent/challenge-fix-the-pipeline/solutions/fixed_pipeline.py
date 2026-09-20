"""Challenge solution: the research pipeline with all three fixes in place.

Fix 1: the coordinator splits the question across every segment, not just the
       most prominent one.
Fix 2: each call is told which segment it owns and which belong to others, so
       no two subagents read the same documents.
Fix 3: the coordinator reviews the report for gaps and re-delegates until
       coverage is complete.

All three fixes live in COORDINATOR_PROMPT. The subagent definitions never
changed, because the subagents were never the problem.

Run it from inside the solutions folder:
    cd solutions
    python fixed_pipeline.py
"""

import asyncio
import sys

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

# coverage.py lives one folder up. This line tells Python to look there too.
sys.path.append("..")
try:
    from coverage import print_coverage
except ImportError:
    sys.exit(
        "Could not find coverage.py. Run this from inside the solutions "
        "folder:\n    cd solutions\n    python fixed_pipeline.py"
    )

MODEL = "claude-sonnet-5"
SOURCES_PATH = "../sources"
AGENT_TOOL_NAMES = ["Agent", "Task"]

# Subagents inherit their tool definitions from the parent, and the tools field
# on an AgentDefinition narrows that inherited set. It cannot add to it. So the
# coordinator's allowed_tools has to cover every tool any subagent needs, even
# though the coordinator never calls Glob, Grep, or Read itself.
SUBAGENT_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + SUBAGENT_TOOLS

QUESTION = "What is the impact of AI on creative industries?"

COORDINATOR_PROMPT = """You are the coordinator of a small research team.

Your job is to answer the research question by delegating to your subagents.
Do not read source files yourself. Delegate.

How to run a research job:

1. Break the question into segments that cover all of it. A question about an
   industry usually spans several distinct segments, and a report that covers
   one segment has not answered the question. List the segments before you
   delegate.
2. Give each call one segment, and name in the prompt which segments belong to
   other calls, so no two subagents read the same documents.
3. Send the findings to report-writer, with the source file name and
   publication date attached to each one.
4. Review the report you get back against the original question. Name any
   segment that is missing or thin. For each gap, send a targeted follow-up to
   source-finder and document-analyst, then ask report-writer for a combined
   report. Repeat until every segment is covered.

Subagents remember nothing between calls and cannot see this conversation, so
write everything a subagent needs into the prompt you send it, including
findings from earlier subagents.

Start your response with a line beginning "SEGMENTS:" listing the segments you
identified, so the split is visible before any delegation happens."""

SOURCE_FINDER = AgentDefinition(
    description=(
        "Finds which source documents are relevant to a given slice of a "
        "research question. Returns file names and a one-line reason for each."
    ),
    prompt=f"""You locate relevant documents. The corpus is in {SOURCES_PATH}.

Use Glob to list the files and Grep to search their contents. Each file starts
with a metadata block containing title, outlet, published date, url, and domain.

Return the files relevant to what you were asked about, with the file name, the
domain field, and one line on why it is relevant. Do not summarize them.""",
    tools=["Glob", "Grep", "Read"],
    model=MODEL,
)

DOCUMENT_ANALYST = AgentDefinition(
    description=(
        "Reads specific source documents and extracts findings with "
        "attribution. Use after source-finder has identified the files."
    ),
    prompt="""You read source documents and pull out findings.

Read the files you were given. Return findings in this format:

  FINDING: one sentence stating what was found
  EVIDENCE: a short quoted phrase or a number from the document
  SOURCE: the file name
  OUTLET: the outlet field from the metadata block
  PUBLISHED: the published date from the metadata block

Every finding carries its source.""",
    tools=["Read", "Grep"],
    model=MODEL,
)

REPORT_WRITER = AgentDefinition(
    description=(
        "Combines findings from other subagents into a final written report. "
        "Needs the findings supplied in its prompt; it has no file access."
    ),
    prompt="""You write the final report from findings handed to you.

You have no file access. Everything you need is in the prompt.

Structure:
  - A short opening that answers the research question directly
  - One section per industry segment covered
  - A Coverage section naming any segment the findings did not address

Keep every claim attached to the outlet and date it came from.""",
    tools=[],
    model=MODEL,
)


async def run_research():
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=COORDINATOR_PROMPT,
        allowed_tools=COORDINATOR_TOOLS,
        agents={
            "source-finder": SOURCE_FINDER,
            "document-analyst": DOCUMENT_ANALYST,
            "report-writer": REPORT_WRITER,
        },
        # Cost and sprawl guards. Leave these in place while you work.
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=3.0,
    )

    final_report = ""
    spawn_count = 0

    async for message in query(prompt=QUESTION, options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        spawn_count = spawn_count + 1
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  -> coordinator spawned: {which}")

        if hasattr(message, "result"):
            final_report = message.result

    print(f"\nSubagents spawned: {spawn_count}")
    return final_report


async def main():
    print(f"Research question: {QUESTION}\n")
    print("Delegation log:")
    report = await run_research()
    print("\n" + "=" * 60)
    print(report)
    print_coverage(report)


if __name__ == "__main__":
    asyncio.run(main())
