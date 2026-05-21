"""Intent router — classifies user query to 1-2 Qdrant collections via Groq."""

from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq

from backend.lib.prompts import ROUTER_SYSTEM
from backend.lib.qdrant_store import COLLECTIONS

ALLOWED = set(COLLECTIONS)


def route(
    query: str,
    force_collections: list[str] | None = None,
    use_case: str | None = None,
    groq_client: Groq | None = None,
    model: str | None = None,
) -> list[str]:
    """Route a query to 1-2 collections.

    If force_collections is set, bypass the LLM router.
    Falls back to all collections on malformed output.
    """
    if force_collections:
        valid = [c for c in force_collections if c in ALLOWED]
        return valid if valid else list(ALLOWED)

    if groq_client is None:
        from backend.lib.settings import settings
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        model = model or settings.GROQ_MODEL

    try:
        response = groq_client.chat.completions.create(
            model=model or "openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM},
                {"role": "user", "content": query},
            ],
            temperature=0,
            max_tokens=100,
        )
        raw = response.choices[0].message.content or ""
        picks = _parse_json_array(raw)
        valid = [c for c in picks if c in ALLOWED]
        return valid[:2] if valid else list(ALLOWED)
    except Exception:
        return list(ALLOWED)


def _parse_json_array(text: str) -> list[str]:
    """Extract a JSON array from text, tolerating surrounding prose."""
    # Try direct parse
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [str(x) for x in result]
    except json.JSONDecodeError:
        pass

    # Try to find array in text
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return [str(x) for x in result]
        except json.JSONDecodeError:
            pass

    return []
