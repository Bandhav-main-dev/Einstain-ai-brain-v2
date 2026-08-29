from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
STATE_FILE = LOG_DIR / "project_state.json"


DEFAULT_STATE: dict[str, Any] = {
    "project": "Einstein AI V2",
    "version": "0.1.0",
    "current_phase": "0.6.1",
    "current_step": "structured-logging-core",
    "status": "in_progress",
    "overall_progress": 0,
    "completed_steps": [],
    "active_steps": [],
    "failed_steps": [],
    "last_update": None,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_state_directory() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    ensure_state_directory()

    if not STATE_FILE.exists():
        save_state(DEFAULT_STATE.copy())
        return DEFAULT_STATE.copy()

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        save_state(DEFAULT_STATE.copy())
        return DEFAULT_STATE.copy()


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    ensure_state_directory()

    state["last_update"] = utc_now()

    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return state


def update_state(**updates: Any) -> dict[str, Any]:
    state = load_state()
    state.update(updates)
    return save_state(state)


def mark_step_completed(
    step: str,
    *,
    phase: str,
    progress: int,
) -> dict[str, Any]:
    state = load_state()

    completed = state.setdefault("completed_steps", [])

    if step not in completed:
        completed.append(step)

    active = state.setdefault("active_steps", [])

    if step in active:
        active.remove(step)

    state["current_phase"] = phase
    state["current_step"] = step
    state["overall_progress"] = progress
    state["status"] = "completed"

    return save_state(state)
