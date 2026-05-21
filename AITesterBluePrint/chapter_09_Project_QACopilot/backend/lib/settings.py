"""Application settings loaded from .env via pydantic-settings."""

import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Required ─────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""

    # ── LLM ──────────────────────────────────────────────────────────
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # ── Qdrant ───────────────────────────────────────────────────────
    QDRANT_PATH: str | None = "./qdrant_data"
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None

    # ── Embedding & rerank ───────────────────────────────────────────
    EMBED_MODEL: str = "BAAI/bge-m3"
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    EMBED_DEVICE: str = "cpu"

    # ── Source paths ─────────────────────────────────────────────────
    SELENIUM_REPO_DIR: Path = Path("./data/selenium_repo")
    SELENIUM_REPO_URL: str = "https://github.com/PramodDutta/ATB14xSeleniumAdvanceFrameworks"
    PLAYWRIGHT_REPO_DIR: Path = Path("./data/playwright_repo")
    PLAYWRIGHT_REPO_URL: str = "https://github.com/PramodDutta/Advance-Playwright-Framework"
    TESTCASES_CSV: Path = Path("./data/csv/VWO_TestCase.csv")
    PDFS_DIR: Path = Path("./data/pdf")
    JIRA_MD_DIR: Path = Path("./data/md")
    GENERATED_DIR: Path = Path("./data/generated")

    # ── Retrieval knobs ──────────────────────────────────────────────
    TOP_K_PER_COLLECTION: int = 12
    RERANK_TOP_K: int = 4
    RERANK_TOP_K_SIMILARITY: int = 8
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    PDF_CHUNK_SIZE: int = 800
    PDF_CHUNK_OVERLAP: int = 120
    HISTORY_TURNS: int = 4
    MIN_RERANK_SCORE: float = 0.3
    SESSION_TTL_MINUTES: int = 30


# Singleton — fail fast if GROQ_API_KEY is missing
settings = Settings()

if not settings.GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY is not set. Add it to .env or environment.", file=sys.stderr)
    sys.exit(1)
