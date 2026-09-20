"""Demo: Pass context without losing sources.

Module 2 wrote findings into a subagent prompt as one blob of text. That works
until a claim needs a citation, and then you find the source was dropped three
handoffs ago.

This demo does it properly. One coordinator runs two subagents in the order it
chooses. The analyst returns findings as labeled fields. The coordinator hands
those fields to the summarizer intact, and the summarizer, which cannot read
files, cites only what it was given.

The part to watch is the prompt the coordinator writes for the summarizer. It
prints below, so you can see exactly what crossed the handoff.

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
# prompt, which is exactly why the coordinator has to carry the metadata over.
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

# The coordinator decides the flow. It is told what a good handoff looks like,
# not which strings to concatenate. Compare this to Module 2, where findings
# went into the writer's prompt as one paragraph and the sources went with it.
COORDINATOR_PROMPT = f"""You are a research coordinator. Answer this question:

                    {QUESTION}

                    Use the document-analyst subagent to extract findings from the policy
                    documents. Then use the summarizer subagent to write the answer.

                    When you hand findings to the summarizer, pass every finding exactly as the
                    analyst returned it, with all five fields intact. Do not summarize the
                    findings, reword them, or drop any field. The summarizer cannot read files,
                    so anything you leave out of its prompt does not exist for it.

                    Return the summarizer's output as your final answer."""


async def main():
    print(f"Question: {QUESTION}\n")

    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=COORDINATOR_PROMPT,
        allowed_tools=COORDINATOR_TOOLS,
        agents={
            "document-analyst": DOCUMENT_ANALYST,
            "summarizer": SUMMARIZER,
        },
        env={
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
            "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4",
        },
        max_budget_usd=3.0,
    )

    summary = ""
    async for message in query(prompt="Begin.", options=options):
        blocks = getattr(message, "content", None)
        if blocks is not None:
            for block in blocks:
                if isinstance(block, ToolUseBlock):
                    if block.name in AGENT_TOOL_NAMES:
                        which = block.input.get("subagent_type", "unknown")
                        print(f"  -> coordinator spawned: {which}")
                        # This is the handoff. Print what the coordinator
                        # wrote so you can see whether the fields survived.
                        if which == "summarizer":
                            print("\n--- prompt the coordinator wrote for the summarizer ---")
                            print(block.input.get("prompt", ""))
                            print("--- end of handoff ---\n")
        if hasattr(message, "result"):
            summary = message.result

    print("=" * 60)
    print(summary)
    print("=" * 60)
    print(
        "\nCheck the citations above against the handoff prompt. Every "
        "document name and page number in the summary should trace back to a "
        "field the analyst produced, not to something the summarizer invented."
    )


if __name__ == "__main__":
    asyncio.run(main())