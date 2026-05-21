"""In-memory session store for multi-turn chat."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    """State for a single chat session."""
    history: list[dict[str, str]] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)
    last_chunks: list[Any] = field(default_factory=list)
    last_message_id: str = ""
    last_use_case: str | None = None
    last_framework: str | None = None
    last_response_text: str = ""


class SessionStore:
    """Thread-safe in-memory session store with TTL eviction."""

    def __init__(self, ttl_minutes: int = 30):
        self._sessions: dict[str, SessionState] = {}
        self._ttl_seconds = ttl_minutes * 60

    def get_or_create(self, session_id: str) -> SessionState:
        """Get existing session or create a new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState()
        session = self._sessions[session_id]
        session.last_seen = time.time()
        return session

    def get_by_message_id(self, message_id: str) -> SessionState | None:
        """Find a session by its last message ID."""
        for session in self._sessions.values():
            if session.last_message_id == message_id:
                return session
        return None

    def evict_stale(self) -> int:
        """Remove sessions older than TTL. Returns count of evicted sessions."""
        now = time.time()
        stale_ids = [
            sid for sid, s in self._sessions.items()
            if (now - s.last_seen) > self._ttl_seconds
        ]
        for sid in stale_ids:
            del self._sessions[sid]
        return len(stale_ids)

    @property
    def active_count(self) -> int:
        return len(self._sessions)
