"""
QA Copilot — Scheduled Ingestion Runner
========================================
Runs backend.ingest.ingest_all.main() on a recurring schedule using APScheduler.

Usage:
    python -m scheduler.scheduler

Configuration (via environment variables or .env):
    INGEST_INTERVAL_MINUTES  — interval between runs in minutes (default: 60)
    INGEST_CRON              — optional cron expression (e.g. "0 * * * *")
                               If set, takes precedence over INGEST_INTERVAL_MINUTES.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Ensure project root is on sys.path (same pattern as ingest scripts) ──────
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(Path(PROJECT_ROOT) / ".env")

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("qa_copilot.scheduler")


# ── Configuration ────────────────────────────────────────────────────────────
INGEST_INTERVAL_MINUTES = int(os.getenv("INGEST_INTERVAL_MINUTES", "60"))
INGEST_CRON = os.getenv("INGEST_CRON", "").strip()


# ── Job function ─────────────────────────────────────────────────────────────
def run_ingest() -> None:
    """Execute the full ingestion pipeline and log results."""
    start = datetime.now(timezone.utc)
    logger.info("Ingestion started at %s", start.isoformat())

    try:
        from backend.ingest.ingest_all import main as ingest_main

        exit_code = ingest_main()
        end = datetime.now(timezone.utc)
        elapsed = (end - start).total_seconds()

        if exit_code == 0:
            logger.info(
                "Ingestion completed successfully in %.1f seconds", elapsed
            )
        else:
            logger.warning(
                "Ingestion finished with failures (exit_code=%d) in %.1f seconds",
                exit_code,
                elapsed,
            )
    except Exception:
        end = datetime.now(timezone.utc)
        elapsed = (end - start).total_seconds()
        logger.exception(
            "Ingestion crashed after %.1f seconds", elapsed
        )


# ── Main entry point ─────────────────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 60)
    logger.info("  QA Copilot — Scheduler starting")
    logger.info("=" * 60)

    # ── Run initial ingest immediately ────────────────────────────────────
    logger.info("Running initial ingestion on startup...")
    run_ingest()

    # ── Build trigger ─────────────────────────────────────────────────────
    if INGEST_CRON:
        logger.info("Using CRON schedule: %s", INGEST_CRON)
        trigger = CronTrigger.from_crontab(INGEST_CRON)
    else:
        logger.info(
            "Using interval schedule: every %d minute(s)", INGEST_INTERVAL_MINUTES
        )
        trigger = IntervalTrigger(minutes=INGEST_INTERVAL_MINUTES)

    # ── Create and configure scheduler ────────────────────────────────────
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_ingest,
        trigger=trigger,
        id="ingest_all",
        name="QA Copilot Ingest All",
        max_instances=1,
        coalesce=True,
    )

    # ── Graceful shutdown on Ctrl+C / SIGTERM ─────────────────────────────
    def _shutdown(signum, frame):
        logger.info("Received signal %s — shutting down scheduler...", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # ── Start blocking loop ───────────────────────────────────────────────
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
