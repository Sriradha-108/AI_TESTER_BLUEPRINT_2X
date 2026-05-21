# QA Copilot — Scheduler

Automated recurring ingestion for the QA Copilot knowledge base using [APScheduler](https://apscheduler.readthedocs.io/).

## What it does

The scheduler calls `backend.ingest.ingest_all.main()` on a configurable interval (or cron schedule), keeping the vector store up-to-date with the latest source data.

**Behaviour:**
1. Runs an **initial ingest immediately** on startup.
2. Schedules recurring runs based on configuration.
3. Logs start/end timestamps and success/failure for every run.
4. Shuts down gracefully on `Ctrl+C` or `SIGTERM`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `INGEST_INTERVAL_MINUTES` | `60` | Minutes between ingestion runs (interval mode) |
| `INGEST_CRON` | _(empty)_ | Cron expression (e.g. `0 * * * *`). If set, **overrides** the interval. |

Set these in your `.env` file at the project root or export them as environment variables.

### Examples

```bash
# Run every 30 minutes
INGEST_INTERVAL_MINUTES=30

# Run at the top of every hour (cron takes precedence)
INGEST_CRON=0 * * * *

# Run daily at 2 AM
INGEST_CRON=0 2 * * *
```

## Running

From the `chapter_09_Project_QACopilot/` directory:

```bash
# Make sure dependencies are installed
pip install -r backend/requirements.txt

# Start the scheduler
python -m scheduler.scheduler
```

Or with Docker / process manager — just ensure the working directory is the chapter root.

## Dependencies

- `APScheduler==3.10.4` (added to `backend/requirements.txt`)
- `python-dotenv` (already in requirements)

## Architecture

```
chapter_09_Project_QACopilot/
├── scheduler/
│   ├── __init__.py
│   ├── scheduler.py      ← entry point
│   └── README.md         ← this file
├── backend/
│   └── ingest/
│       └── ingest_all.py ← called by the scheduler
└── .env                  ← configuration
```
