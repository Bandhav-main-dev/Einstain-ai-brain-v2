from __future__ import annotations

from typing import Any

from .logging_core import log_event, read_events
from .project_state import load_state, save_state

TOTAL_ENGINEERING_STEPS = 100


def record_progress(
    *,
    phase: str,
    step: str,
    progress: int,
    message: str,
    status: str = "IN_PROGRESS",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    progress = max(0, min(100, progress))

    event = log_event(
        "progress",
        message,
        phase=phase,
        step=step,
        status=status,
        data=data,
    )

    state = load_state()

    state["current_phase"] = phase
    state["current_step"] = step
    state["overall_progress"] = progress
    state["status"] = status.lower()

    save_state(state)

    return event


def get_progress_summary() -> dict[str, Any]:
    state = load_state()
    events = read_events()

    return {
        "project": state["project"],
        "version": state["version"],
        "phase": state["current_phase"],
        "step": state["current_step"],
        "status": state["status"],
        "overall_progress": state["overall_progress"],
        "completed_steps": state["completed_steps"],
        "active_steps": state["active_steps"],
        "failed_steps": state["failed_steps"],
        "event_count": len(events),
        "last_update": state["last_update"],
    }
