from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .logging_core import log_event, read_events
from .project_state import load_state, save_state

TOTAL_ENGINEERING_STEPS = 100


def _utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: float) -> float:
    """Clamp progress to the valid 0-100 range."""
    return max(0.0, min(100.0, float(value)))


def calculate_overall_progress(
    completed_steps: list[str],
    active_steps: list[str],
    total_steps: int = TOTAL_ENGINEERING_STEPS,
) -> float:
    """
    Calculate project progress from completed and active steps.

    Completed steps contribute one full unit.
    Active steps contribute half a unit.
    """
    if total_steps <= 0:
        return 0.0

    completed = len(set(completed_steps))
    active = len(set(active_steps) - set(completed_steps))

    progress = ((completed + (active * 0.5)) / total_steps) * 100.0

    return round(_clamp(progress), 2)


def calculate_step_progress(
    completed: bool = False,
    active: bool = False,
    progress_percent: float | None = None,
) -> float:
    """Calculate normalized progress for one engineering step."""

    if progress_percent is not None:
        return round(_clamp(progress_percent), 2)

    if completed:
        return 100.0

    if active:
        return 50.0

    return 0.0


def update_step(
    step_id: str,
    status: str,
    progress_percent: float | None = None,
    message: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Update the project state for an engineering step.

    Valid statuses:
        planned
        active
        completed
        blocked
        failed
    """
    valid_statuses = {
        "planned",
        "active",
        "completed",
        "blocked",
        "failed",
    }

    if status not in valid_statuses:
        raise ValueError(f"Invalid step status: {status}")

    state = load_state()

    completed_steps = list(state.get("completed_steps", []))

    active_steps = list(state.get("active_steps", []))

    if status == "completed":
        if step_id not in completed_steps:
            completed_steps.append(step_id)

        active_steps = [step for step in active_steps if step != step_id]

    elif status == "active":
        if step_id not in active_steps:
            active_steps.append(step_id)

        completed_steps = [step for step in completed_steps if step != step_id]

    elif status in {"blocked", "failed"}:
        active_steps = [step for step in active_steps if step != step_id]

    state["completed_steps"] = sorted(set(completed_steps))

    state["active_steps"] = sorted(set(active_steps))

    state["overall_progress"] = calculate_overall_progress(
        state["completed_steps"],
        state["active_steps"],
    )

    state["progress_percent"] = state["overall_progress"]
    state["updated_at"] = _utc_now()

    save_state(state)

    event = log_event(
        event_type="progress_update",
        phase=state.get("current_phase", ""),
        step=step_id,
        status=status,
        progress_percent=(
            calculate_step_progress(
                completed=status == "completed",
                active=status == "active",
                progress_percent=progress_percent,
            )
        ),
        message=message,
        metadata=metadata or {},
    )

    return {
        "step_id": step_id,
        "status": status,
        "step_progress": event.get(
            "progress_percent",
            0.0,
        ),
        "overall_progress": state["overall_progress"],
        "event_id": event.get("event_id"),
    }


def record_test_result(
    passed: int = 0,
    failed: int = 0,
    warnings: int = 0,
    errors: int = 0,
    message: str = "",
) -> dict[str, Any]:
    """Record test and validation results in project state."""

    if (
        min(
            passed,
            failed,
            warnings,
            errors,
        )
        < 0
    ):
        raise ValueError("Test result counts cannot be negative.")

    state = load_state()

    state["tests_passed"] = int(state.get("tests_passed", 0)) + passed

    state["tests_failed"] = int(state.get("tests_failed", 0)) + failed

    state["warnings"] = int(state.get("warnings", 0)) + warnings

    state["errors"] = int(state.get("errors", 0)) + errors

    state["updated_at"] = _utc_now()

    save_state(state)

    return log_event(
        event_type="test_result",
        phase=state.get("current_phase", ""),
        step=state.get("current_step", ""),
        status="completed" if failed == 0 else "failed",
        message=message,
        metadata={
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "errors": errors,
        },
    )


def get_progress_summary() -> dict[str, Any]:
    """Return a dashboard-ready progress summary."""

    state = load_state()
    events = read_events()

    completed = state.get(
        "completed_steps",
        [],
    )

    active = state.get(
        "active_steps",
        [],
    )

    return {
        "project": state.get(
            "project",
            "Einstein AI V2",
        ),
        "version": state.get(
            "version",
            "0.1.0",
        ),
        "current_phase": state.get(
            "current_phase",
            "",
        ),
        "current_step": state.get(
            "current_step",
            "",
        ),
        "status": state.get(
            "status",
            "UNKNOWN",
        ),
        "overall_progress": state.get(
            "overall_progress",
            state.get(
                "progress_percent",
                0.0,
            ),
        ),
        "completed_steps": completed,
        "active_steps": active,
        "completed_count": len(completed),
        "active_count": len(active),
        "tests_passed": state.get(
            "tests_passed",
            0,
        ),
        "tests_failed": state.get(
            "tests_failed",
            0,
        ),
        "warnings": state.get(
            "warnings",
            0,
        ),
        "errors": state.get(
            "errors",
            0,
        ),
        "event_count": len(events),
        "updated_at": state.get(
            "updated_at",
            "",
        ),
    }
