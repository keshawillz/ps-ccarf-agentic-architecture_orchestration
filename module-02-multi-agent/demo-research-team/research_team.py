"""Demo: Build a research team with the Claude Agent SDK.

Module 1 wrote the loop by hand. Here the SDK runs the loop for us, and our
job moves up a level: describe the team, then let the coordinator decide who
works on what.

Three subagents:
    source-finder     finds relevant documents in the sources folder
    document-analyst  reads them and pulls out findings with attribution
    report-writer     combines the findings into one report

Run it:
    python research_team.py
    python research_team.py "your own research question"
"""

import asyncio
import sys

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ToolUseBlock,
    query,
)

MODEL = "claude-sonnet-5"

# The sources folder sits one level up, shared by both demos and the challenge.
SOURCES_PATH = "../sources"

# Claude invokes subagents through a built-in tool. The exam calls it the Task
# tool. Claude Code renamed it to "Agent" in v2.1.63, and current releases emit
# "Agent" in tool_use blocks while still listing "Task" in system:init. Match
# both names so this works on either version.
AGENT_TOOL_NAMES = ["Agent", "Task"]

# The coordinator's allowed_tools has to include every tool its subagents
# use, even ones the coordinator never calls itself. allowed_tools is a
# permission allowlist, and in a non-interactive run a subagent's call to an
# unlisted tool is denied rather than prompted. Tested on this SDK version;
# how subagents inherit tools and permissions has open bugs, so re-verify
# after upgrading.
SUBAGENT_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + SUBAGENT_TOOLS

COORDINATOR_PROMPT = """You are the coordinator of a small research team.

Your job is to answer the research question by delegating to your subagents.
Do not read source files yourself. Delegate.

How to run a research job:

1. Decide which parts of the question need investigating. Cover the whole
   question, not just the first area that comes to mind. A question about an
   industry usually has several distinct segments, and missing one means the
   report is incomplete.
2. Give each source-finder and document-analyst call its own slice of the
   question. Say in the prompt which slice it owns and which slices belong to
   other subagents, so two subagents never analyze the same document.
3. Subagents start with no memory of this conversation. Whatever a subagent
   needs to know has to be written into the prompt you send it, including any
   findings from earlier subagents.
4. When you have findings, send them to report-writer. Include the findings
   themselves in the prompt, with the source file name and publication date
   attached to each one.

Aim for complete coverage of the question and accurate attribution on every
claim."""

SOURCE_FINDER = AgentDefinition(
    description=(
        "Finds which source documents are relevant to a given slice of a "
        "research question. Use this first, before any analysis. Returns file "
        "names and a one-line reason for each. Does not summarize content."
    ),
    prompt=f"""You locate relevant documents. The corpus is in {SOURCES_PATH}.

Use Glob to list the files and Grep to search their contents. Each file starts
with a metadata block containing title, outlet, published date, url, and domain.

You will be given one slice of a research question. Return only the files
relevant to your slice, as a list. For each file give the file name, the
domain field, and one line on why it is relevant.

Do not summarize the documents. Finding them is your whole job.""",
    tools=["Glob", "Grep", "Read"],
    model=MODEL,
)

DOCUMENT_ANALYST = AgentDefinition(
    description=(
        "Reads specific source documents and extracts findings with "
        "attribution. Use after source-finder has identified which files "
        "matter. Returns findings, each tied to its source file and date."
    ),
    prompt="""You read source documents and pull out findings.

You will be given a list of file names and the slice of the research question
you are responsible for. Read those files. Do not read files outside your list,
because another subagent is covering them.

Return findings in this format, one block per finding:

  FINDING: one sentence stating what was found
  EVIDENCE: a short quoted phrase or a number from the document
  SOURCE: the file name
  OUTLET: the outlet field from the metadata block
  PUBLISHED: the published date from the metadata block

Attribution is not optional. A finding without its source is unusable to the
person writing the report.""",
    tools=["Read", "Grep"],
    model=MODEL,
)

REPORT_WRITER = AgentDefinition(
    description=(
        "Combines findings from other subagents into a final written report. "
        "Use last, after analysis is complete. Needs the findings supplied in "
        "its prompt; it cannot read source files itself."
    ),
    prompt="""You write the final report from findings handed to you.

You have no file access. Everything you need is in the prompt. If a topic area
is missing from the findings, say so in a Coverage section rather than filling
the gap from your own knowledge.

Structure the report as:
  - A short opening that answers the research question directly
  - One section per industry segment covered
  - A Coverage section naming any segment the findings did not address

Keep every claim attached to the outlet and date it came from.""",
    tools=[],
    model=MODEL,
)

DEFAULT_QUESTION = "What is the impact of AI on creative industries?"


async def run_research(question):
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=COORDINATOR_PROMPT,
        # The coordinator needs the Agent tool to delegate. Its file tools are
        # here because subagents inherit from the parent and can only narrow
        # that set, so the parent has to hold everything they need.
        allowed_tools=COORDINATOR_TOOLS,
        agents={
            "source-finder": SOURCE_FINDER,
            "document-analyst": DOCUMENT_ANALYST,
            "report-writer": REPORT_WRITER,
        },
        # Guard rails. Subagents can spawn subagents, so one question can turn
        # into a tree of agents and a surprising bill. These three caps keep a
        # demo run predictable.
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=2.0,
    )

    final_report = ""
    async for message in query(prompt=question, options=options):
        # Watch the coordinator delegate. Every spawn shows up as a tool call.
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  -> coordinator spawned: {which}")

        if hasattr(message, "result"):
            final_report = message.result

    return final_report


async def main():
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = DEFAULT_QUESTION

    print(f"Research question: {question}\n")
    print("Delegation log:")
    report = await run_research(question)
    print("\n" + "=" * 60)
    print(report)


# query() is asynchronous, so it has to run inside an async function.
# asyncio.run starts one and waits for it to finish. That is the only
# async machinery in this file.
if __name__ == "__main__":
    asyncio.run(main())
