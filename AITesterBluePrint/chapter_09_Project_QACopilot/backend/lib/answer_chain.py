"""Answer chain — streams cited answers from Groq with retry logic."""

from __future__ import annotations

import asyncio
import re
from typing import Any, AsyncIterator

from groq import AsyncGroq

from backend.lib.prompts import ANSWER_SYSTEM, render_context
from backend.lib.retriever import ScoredChunk


def detect_use_case(query: str, framework: str | None = None) -> str | None:
    """Detect the use case from the rewritten query.

    Returns one of: "generate_tc", "find_similar", "generate_code", or None.
    """
    q = query.lower()

    # UC1: Generate test cases from JIRA
    if re.search(r"\b(generate|create|write)\b.*\b(test case|tc|test)\b", q):
        if re.search(r"\b(kan-\d+|jira|ticket|bug)\b", q):
            return "generate_tc"

    # UC3: Generate automation code
    if re.search(r"\b(generate|create|write)\b.*\b(code|script|automation|selenium|playwright)\b", q):
        return "generate_code"
    if framework and framework != "auto":
        if re.search(r"\b(generate|create|write)\b", q):
            return "generate_code"

    # UC2: Find similar test cases
    if re.search(r"\b(similar|find|do we have|existing|duplicate|already)\b.*\b(test|tc)\b", q):
        return "find_similar"
    if re.search(r"\b(test|tc)\b.*\b(similar|exist|already|duplicate)\b", q):
        return "find_similar"

    # UC1 fallback: generate test cases (no JIRA reference)
    if re.search(r"\b(generate|create|write)\b.*\b(test case|tc|test)\b", q):
        return "generate_tc"

    return None


async def stream_answer(
    user_query: str,
    rewritten_query: str,
    history: list[dict[str, str]],
    chunks: list[ScoredChunk],
    use_case: str | None = None,
    framework: str | None = None,
    groq_api_key: str | None = None,
    model: str | None = None,
) -> AsyncIterator[str]:
    """Stream answer tokens from Groq.

    Yields individual token strings. Handles retry with exponential backoff.
    """
    if groq_api_key is None:
        from backend.lib.settings import settings
        groq_api_key = settings.GROQ_API_KEY
        model = model or settings.GROQ_MODEL

    # Build context from chunks
    chunk_dicts = [c.payload for c in chunks]
    context = render_context(chunk_dicts)

    # Build system prompt with use-case hints
    system = ANSWER_SYSTEM
    if use_case == "generate_tc":
        system += "\n\nThe user wants to GENERATE NEW TEST CASES. Output them in CSV/table format."
    elif use_case == "generate_code":
        fw = framework or "the appropriate"
        system += f"\n\nThe user wants to GENERATE AUTOMATION CODE in {fw}. Output a complete runnable file in a fenced code block."
    elif use_case == "find_similar":
        system += "\n\nThe user wants to FIND SIMILAR/EXISTING TEST CASES. List matches as bullets with TC_ID — Name — summary [N]."

    # Build messages
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]

    # Add recent history for continuity
    for turn in history[-8:]:
        messages.append(turn)

    # Add context + user query
    user_content = f"Context:\n{context}\n\n---\n\nUser question: {user_query}"
    messages.append({"role": "user", "content": user_content})

    # Stream with retry
    client = AsyncGroq(api_key=groq_api_key)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            stream = await client.chat.completions.create(
                model=model or "openai/gpt-oss-120b",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
            return  # Success
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                await asyncio.sleep(wait)
            else:
                yield f"\n\n[Error: Failed after {max_retries} retries: {e}]"
