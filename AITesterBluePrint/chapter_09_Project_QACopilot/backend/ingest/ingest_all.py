"""Orchestrator: runs all five ingest scripts in order."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.ingest import ingest_selenium, ingest_playwright, ingest_testcases, ingest_pdfs, ingest_jira


STEPS = [
    ("selenium", ingest_selenium.main),
    ("playwright", ingest_playwright.main),
    ("testcases", ingest_testcases.main),
    ("pdfs", ingest_pdfs.main),
    ("jira", ingest_jira.main),
]


def main() -> int:
    print("=" * 60)
    print("  QA Copilot — Ingest All Sources")
    print("=" * 60)

    results: dict[str, str] = {}
    failures: list[str] = []

    for name, fn in STEPS:
        print(f"\n{'─' * 40}")
        print(f"  Ingesting: {name}")
        print(f"{'─' * 40}")
        try:
            fn()
            results[name] = "✓ success"
        except Exception:
            traceback.print_exc()
            results[name] = "✗ FAILED"
            failures.append(name)

    # Summary table
    print(f"\n{'═' * 60}")
    print("  INGEST SUMMARY")
    print(f"{'═' * 60}")
    for name, status in results.items():
        print(f"  {name:<15} {status}")
    print(f"{'─' * 60}")
    print(f"  Total: {len(STEPS) - len(failures)}/{len(STEPS)} succeeded")
    if failures:
        print(f"  Failed: {', '.join(failures)}")
    print(f"{'═' * 60}")

    return 0 if not failures else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
