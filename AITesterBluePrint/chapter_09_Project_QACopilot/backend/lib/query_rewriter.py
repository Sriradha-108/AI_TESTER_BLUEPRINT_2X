"""Query rewriter — condenses multi-turn conversation into a standalone query."""

from __future__ import annotations

from typing import Any

from groq import Groq

from backend.lib.prompts import REWRITE_SYSTEM


def rewrite(
    history: list[dict[str, str]],
    latest: str,
    groq_client: Groq | None = None,
    model: str | None = None,
) -> str:
    """Rewrite the latest user message into a standalone query using conversation history.

    If no history, returns the latest message as-is.
    """
    if not history:
        return latest

    if groq_client is None:
        from backend.lib.settings import settings
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        model = model or settings.GROQ_MODEL

    # Format recent history
    from backend.lib.settings import settings as s
    turns = history[-(s.HISTORY_TURNS * 2):]  # Each turn is user+assistant
    convo_lines = []
    for turn in turns:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        convo_lines.append(f"{role.capitalize()}: {content[:200]}")

    convo_text = "\n".join(convo_lines)
    user_prompt = f"Conversation so far:\n{convo_text}\n\nLatest user message: {latest}"

    try:
        response = groq_client.chat.completions.create(
            model=model or "openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=200,
        )
        rewritten = response.choices[0].message.content or latest
        return rewritten.strip()
    except Exception:
        return latest
