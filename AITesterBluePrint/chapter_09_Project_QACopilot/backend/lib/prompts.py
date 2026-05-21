"""System prompts for router, query rewriter, and answer generation."""

from __future__ import annotations

from typing import Any

ROUTER_SYSTEM = """You are a router that picks 1-2 source collections for a QA query.
Available collections:
- selenium_code: Java/TestNG framework code (page objects, helpers, test classes)
- playwright_code: TypeScript Playwright framework (fixtures, specs, page objects)
- vwo_testcases: Manual test case specifications for app.vwo.com login flows
- vwo_docs: VWO product PRDs and feature specs (PDFs)
- vwo_bugs: JIRA bug exports (KAN-N tickets)

Examples:
Q: Show how login fixture is set up in Playwright
A: ["playwright_code"]
Q: List P0 test cases for login
A: ["vwo_testcases"]
Q: Generate Selenium code for TC_LOGIN_009
A: ["vwo_testcases", "selenium_code"]
Q: What does the PRD say about 2FA?
A: ["vwo_docs"]
Q: Open bugs for login failures
A: ["vwo_bugs"]
Q: Generate test cases from KAN-3
A: ["vwo_bugs", "vwo_testcases"]
Q: Do we have a test for SQL injection?
A: ["vwo_testcases"]
Q: How does the Selenium BasePage work?
A: ["selenium_code"]

Return ONLY a JSON array of 1 or 2 collection names. No prose."""

REWRITE_SYSTEM = """Rewrite the user's latest question into a standalone query
that includes any context implied by recent conversation. Output ONLY the
rewritten query, no preamble."""

ANSWER_SYSTEM = """You are QA Copilot, an expert QA engineer assistant for app.vwo.com.

You are given context chunks tagged like:
<doc id="1" source_type="..." source_path="..." ...metadata...>
text
</doc>

Rules:
- Ground every claim in the provided context. Cite each claim with [N] where N is the doc id.
- If the context is insufficient, say so explicitly. Do not invent.
- For test case generation: output rows in a markdown table or CSV format with columns Test Case ID, Test Case Name, Precondition, Test Steps, Expected Result, Priority.
- For code generation: output a complete file in a fenced ```java or ```typescript block, matching the conventions visible in the cited code chunks (page objects, base classes, fixtures, naming).
- For similarity searches: list each hit as a bullet "TC_ID — Name — one-line summary [N]".
- Keep answers concise and actionable."""


def render_context(chunks: list[dict[str, Any]]) -> str:
    """Render scored chunks into <doc> tagged blocks for the LLM context."""
    blocks = []
    for i, chunk in enumerate(chunks, 1):
        payload = chunk.get("payload", chunk)
        source_type = payload.get("source_type", "unknown")
        source_path = payload.get("source_path", "")

        # Build metadata attributes
        attrs = [f'id="{i}"', f'source_type="{source_type}"', f'source_path="{source_path}"']

        # Add type-specific metadata
        if source_type in ("selenium_code", "playwright_code"):
            if payload.get("symbol"):
                attrs.append(f'symbol="{payload["symbol"]}"')
            if payload.get("kind"):
                attrs.append(f'kind="{payload["kind"]}"')
            if payload.get("start_line"):
                attrs.append(f'lines="{payload["start_line"]}-{payload.get("end_line", "")}"')
        elif source_type == "vwo_testcases":
            if payload.get("tc_id"):
                attrs.append(f'tc_id="{payload["tc_id"]}"')
            if payload.get("priority"):
                attrs.append(f'priority="{payload["priority"]}"')
        elif source_type == "vwo_docs":
            if payload.get("doc_title"):
                attrs.append(f'doc_title="{payload["doc_title"]}"')
            if payload.get("page"):
                attrs.append(f'page="{payload["page"]}"')
            if payload.get("section"):
                attrs.append(f'section="{payload["section"]}"')
        elif source_type == "vwo_bugs":
            if payload.get("jira_id"):
                attrs.append(f'jira_id="{payload["jira_id"]}"')
            if payload.get("status"):
                attrs.append(f'status="{payload["status"]}"')
            if payload.get("priority"):
                attrs.append(f'priority="{payload["priority"]}"')

        attr_str = " ".join(attrs)
        text = payload.get("text", "")
        blocks.append(f"<doc {attr_str}>\n{text}\n</doc>")

    return "\n\n".join(blocks)
