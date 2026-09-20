"""Clip 3: Pass context without losing sources.

Module 2 wrote findings into a subagent prompt as one blob of text. That works
until a claim needs a citation, and then you find the source was dropped three
handoffs ago.

This demo does it properly. The analyst returns findings as labeled fields,
your code hands them over with the labels intact, and the summary subagent
receives content and attribution as separate fields rather than as prose it
has to untangle.

Run it:
    python context_handoff.py
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
SUBAGENT_TOOLS = ["Glob", "Grep", "Read"]
COORDINATOR_TOOLS = AGENT_TOOL_NAMES + SUBAGENT_TOOLS

QUESTION = (
    "A customer says they were charged twice on the same day for the same "
    "amount. What should a support agent check, and when should this be "
    "escalated?"
)

# The analyst returns one block per finding, with fixed field names. Fixed
# field names are what keep the metadata attached to its claim through the
# handoff, instead of trailing off into a sentence that gets summarized away.
DOCUMENT_ANALYST = AgentDefinition(
    description=(
        "Reads policy documents and extracts findings with full attribution, "
        "including document name, page number, and publication date."
    ),
    prompt=f"""You read policy documents and extract findings.

The documents are in {SOURCES_PATH}. Each file starts with a metadata block
containing title, document, published, and pages. The body is marked with
[page N] markers.

Return one block per finding, using exactly these field names:

  CLAIM: one sentence stating what the document says
  QUOTE: a short phrase copied from the document
  DOCUMENT: the document field from the metadata block
  PAGE: the page number the claim came from, read from the [page N] marker
  PUBLISHED: the published field from the metadata block

The PAGE field is not optional. Find the [page N] marker above the text you
used. A claim whose page cannot be traced is a claim the reader cannot check.""",
    tools=SUBAGENT_TOOLS,
    model=MODEL,
)

# The summarizer has no file access at all. Everything it knows arrives in the
# prompt, which is exactly why the prompt has to carry the metadata.
SUMMARIZER = AgentDefinition(
    description=(
        "Writes a short guidance summary from findings supplied in its prompt. "
        "Has no file access and cannot look anything up."
    ),
    prompt="""You write short guidance for support agents.

You will be given findings, each with a CLAIM, QUOTE, DOCUMENT, PAGE, and
PUBLISHED field. Write two or three short paragraphs answering the question.

After every sentence that uses a finding, cite it inline as
(DOCUMENT, page PAGE). Use the exact document name and page number you were
given. You have no file access, so you cannot check or correct them, and you
must not invent a citation for a claim that did not come with one.""",
    tools=[],
    model=MODEL,
)


def format_findings(raw_findings_text):
    """Wrap the analyst's output in a labeled section for the summarizer.

    The findings already carry their metadata as named fields. This function's
    job is to hand them over without flattening them into prose, and to say
    plainly what the fields mean. Compare that to pasting the analyst's whole
    reply into the prompt and hoping the citations survive.
    """
    header = (
        "The findings below come from a document analyst.\n"
        "Each one has these fields:\n"
        "  CLAIM      what the document says\n"
        "  QUOTE      exact words from the document\n"
        "  DOCUMENT   the file the claim came from\n"
        "  PAGE       the page within that file\n"
        "  PUBLISHED  when the document was published\n"
        "\n"
        "Treat DOCUMENT and PAGE as the citation for the claim above them.\n"
        "\n"
    )
    return header + raw_findings_text


async def run_subagent(agent_name, agent_def, task_prompt):
    """Run one subagent and return the text it produced."""
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=(
            "You are a coordinator. Delegate the task to the named subagent "
            "and return that subagent's findings verbatim. Do not summarize "
            "or reword them."
        ),
        allowed_tools=COORDINATOR_TOOLS,
        agents={agent_name: agent_def},
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=2.0,
    )

    result_text = ""
    async for message in query(prompt=task_prompt, options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  -> spawned: {which}")
        if hasattr(message, "result"):
            result_text = message.result
    return result_text


async def main():
    print(f"Question: {QUESTION}\n")

    print("Step 1: analyst reads the policy documents")
    analyst_task = (
        "Use the document-analyst subagent. Ask it to read every file in "
        f"{SOURCES_PATH} and extract findings relevant to this question:\n\n"
        f"{QUESTION}\n\n"
        "Return its findings exactly as written."
    )
    findings = await run_subagent(
        "document-analyst", DOCUMENT_ANALYST, analyst_task
    )
    print("\n--- findings as returned ---")
    print(findings)

    print("\nStep 2: hand the findings over with their metadata intact")
    summarizer_task = (
        "Use the summarizer subagent. Send it exactly the text below as its "
        "prompt, then return its summary.\n\n"
        + format_findings(findings)
        + f"\n\nQuestion to answer: {QUESTION}"
    )
    summary = await run_subagent("summarizer", SUMMARIZER, summarizer_task)

    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60)
    print(
        "\nCheck the citations above against the findings. Every document "
        "name and page number should trace back to a field the analyst "
        "produced, not to something the summarizer invented."
    )


if __name__ == "__main__":
    asyncio.run(main())
