from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
EVENT_LOG = LOG_DIR / "project_events.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_log_directory() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_event(
    event_type: str,
    message: str,
    *,
    phase: str | None = None,
    step: str | None = None,
    status: str = "INFO",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_log_directory()

    event = {
        "timestamp": utc_now(),
        "event_type": event_type,
        "message": message,
        "phase": phase,
        "step": step,
        "status": status,
        "data": data or {},
    }

    with EVENT_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


def read_events() -> list[dict[str, Any]]:
    ensure_log_directory()

    if not EVENT_LOG.exists():
        return []

    events: list[dict[str, Any]] = []

    with EVENT_LOG.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events
