"""Challenge starter: a research pipeline that misses topics and repeats work.

Reported from "production":
  1. Reports come back covering one corner of the question.
  2. Two subagents keep reading the same documents.
  3. Nothing ever notices that the report is incomplete.

Your job (see README.md):
  Task 1: fix how the coordinator splits the question.
  Task 2: give each subagent its own slice so no work is repeated.
  Task 3: add a review step that finds gaps and fills them.

Run it:
    python broken_pipeline.py
"""

import asyncio

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

from coverage import print_coverage

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

# BUG 1: the split is too narrow. This tells the coordinator to pick the single
# most prominent area and break that one into subtopics. Every subtopic then
# lands inside one segment of the industry, and the rest of the question never
# gets investigated. The subagents will do their jobs correctly. The problem is
# what they were asked to do.
#
# BUG 2: nothing here tells the coordinator to divide the documents between
# subagents, so each one searches the whole corpus and they cover the same
# ground twice.
#
# BUG 3: there is no review step. The first report the team produces is the
# report that ships, whether or not it answered the question.
COORDINATOR_PROMPT = """You are the coordinator of a small research team.

Your job is to answer the research question by delegating to your subagents.
Do not read source files yourself. Delegate.

How to run a research job:

1. Identify the most prominent area of the question and break that area into
   two or three subtopics. Focus gives a better report than breadth.
2. Send each subtopic to source-finder, then send the results to
   document-analyst.
3. Send the findings to report-writer and return the report it produces.

Subagents remember nothing between calls and cannot see this conversation, so
write everything a subagent needs into the prompt you send it."""

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
