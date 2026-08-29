"""
Einstein AI V2 — Owner Zanpakutō Command Center.

Owner-focused project control dashboard.

The dashboard reads project_control.json as the project roadmap
source of truth.

Responsive layout:
- Desktop / laptop: two-column roadmap grid.
- Mobile: single-column stacked roadmap.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

# =============================================================================
# OWNER COMMAND CENTER
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OWNER_FILE = Path(__file__)

STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"
CONTROL_FILE = PROJECT_ROOT / "monitor" / "project_control.json"


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Einstein AI V2 — Zanpakutō Command Center",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# DATA LOADERS
# =============================================================================

def load_state() -> dict[str, Any]:
    """Load project state safely."""
    if not STATE_FILE.exists():
        return {}

    try:
        data = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )

        return data if isinstance(data, dict) else {}

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
    ):
        return {}


def load_events() -> list[dict[str, Any]]:
    """Load project events with newest events first."""
    if not EVENT_FILE.exists():
        return []

    events: list[dict[str, Any]] = []

    try:
        for line in EVENT_FILE.read_text(
            encoding="utf-8"
        ).splitlines():

            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            if isinstance(item, dict):
                events.append(item)

    except OSError:
        return []

    return list(reversed(events))


def load_project_control() -> dict[str, Any]:
    """Load project_control.json safely."""
    if not CONTROL_FILE.exists():
        return {}

    try:
        data = json.loads(
            CONTROL_FILE.read_text(encoding="utf-8")
        )

        return data if isinstance(data, dict) else {}

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
    ):
        return {}


def git_info() -> dict[str, str]:
    """Return lightweight Git information."""
    def run_git(*args: str) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            return result.stdout.strip()

        except OSError:
            return ""

    return {
        "branch": run_git("branch", "--show-current") or "unknown",
        "commit": run_git("rev-parse", "--short", "HEAD") or "unknown",
        "status": run_git("status", "--short", "--branch"),
    }


# =============================================================================
# NORMALIZATION
# =============================================================================

def get_steps(control: dict[str, Any]) -> list[dict[str, Any]]:
    """Find roadmap steps regardless of the JSON container name."""
    candidates = (
        control.get("steps"),
        control.get("roadmap"),
        control.get("roadmap_steps"),
        control.get("project_steps"),
    )

    for candidate in candidates:
        if isinstance(candidate, list):
            return [
                item
                for item in candidate
                if isinstance(item, dict)
            ]

    return []


def step_title(step: dict[str, Any], index: int) -> str:
    """Get a readable step title."""
    return str(
        step.get("title")
        or step.get("name")
        or step.get("step_name")
        or step.get("phase")
        or f"Project Step {index}"
    )


def step_status(step: dict[str, Any]) -> str:
    """Normalize roadmap status."""
    value = str(
        step.get("status")
        or step.get("state")
        or "not_started"
    ).strip().lower()

    if value in {
        "complete",
        "completed",
        "done",
        "finished",
    }:
        return "completed"

    if value in {
        "active",
        "in_progress",
        "in-progress",
        "working",
    }:
        return "active"

    if value in {
        "blocked",
        "block",
        "waiting",
    }:
        return "blocked"

    return "not_started"


def status_label(status: str) -> str:
    """Human-readable status."""
    return {
        "completed": "COMPLETED",
        "active": "ACTIVE",
        "blocked": "BLOCKED",
        "not_started": "NOT STARTED",
    }.get(status, "NOT STARTED")


def status_symbol(status: str) -> str:
    """Status symbol."""
    return {
        "completed": "✓",
        "active": "◆",
        "blocked": "!",
        "not_started": "○",
    }.get(status, "○")


def step_progress(step: dict[str, Any]) -> float:
    """Get step progress as a percentage."""
    value = (
        step.get("progress")
        if step.get("progress") is not None
        else step.get("progress_percent", 0)
    )

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(0.0, min(100.0, value))


def text_value(
    step: dict[str, Any],
    *keys: str,
    default: str = "Not specified",
) -> str:
    """Return the first meaningful textual field."""
    for key in keys:
        value = step.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, list) and value:
            return " • ".join(str(item) for item in value)

    return default


def overall_progress(
    control: dict[str, Any],
    steps: list[dict[str, Any]],
) -> float:
    """Determine overall project progress."""
    for key in (
        "overall_progress",
        "overall_progress_percent",
        "progress",
        "progress_percent",
    ):
        value = control.get(key)

        if value is not None:
            try:
                return max(0.0, min(100.0, float(value)))
            except (TypeError, ValueError):
                pass

    if not steps:
        return 0.0

    return sum(step_progress(step) for step in steps) / len(steps)


def first_active_step(
    steps: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return active step, otherwise first unfinished step."""
    for step in steps:
        if step_status(step) == "active":
            return step

    for step in steps:
        if step_status(step) != "completed":
            return step

    return None


# =============================================================================
# BLEACH / ZANPAKUTO THEME
# =============================================================================

def inject_theme() -> None:
    """Legacy compatibility hook.

    The dashboard now uses Streamlit-native components only.
    No HTML or custom CSS is injected.
    """
    return


def roadmap_card(
    step: dict[str, Any],
    index: int,
) -> None:
    """Render a roadmap step using native Streamlit components."""

    title = step_title(
        step,
        index + 1,
    )

    status = step_status(step)

    progress = step_progress(step)

    description = text_value(
        step,
        "description",
        "summary",
        "details",
        default="No description available.",
    )

    st.subheader(
        f"{index + 1}. {title}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Status",
            status_label(status),
        )

    with col2:
        st.metric(
            "Progress",
            f"{progress:.0f}%",
        )

    st.progress(
        progress / 100.0
    )

    if description:
        st.caption(
            description
        )

def render_step_details(
    step: dict[str, Any],
) -> None:
    """Render detailed step information using native Streamlit."""

    title = step_title(
        step,
        1,
    )

    status = step_status(step)

    progress = step_progress(step)

    st.subheader(
        title
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Status",
            status_label(status),
        )

    with col2:
        st.metric(
            "Progress",
            f"{progress:.0f}%",
        )

    st.progress(
        progress / 100.0
    )

    description = text_value(
        step,
        "description",
        "summary",
        default="",
    )

    if description:
        st.write(
            description
        )

    details = text_value(
        step,
        "details",
        "detail",
        "notes",
        "explanation",
        default="",
    )

    if details:

        with st.expander(
            "Step Details",
            expanded=True,
        ):
            st.write(
                details
            )

    result = text_value(
        step,
        "result",
        "output",
        "outcome",
        default="",
    )

    if result:

        with st.expander(
            "Result",
        ):
            st.write(
                result
            )


# =============================================================================
# DASHBOARD
# =============================================================================

def render_dashboard() -> None:
    """Render the Einstein AI V2 owner dashboard."""

    # =====================================================================
    # PAGE TITLE
    # =====================================================================

    st.title(
        "⚔️ Einstein AI V2"
    )

    st.caption(
        "⚔️ ZANPAKUTŌ COMMAND CENTER · OWNER MONITORING"
    )

    # =====================================================================
    # LOAD PROJECT DATA
    # =====================================================================

    try:
        control = load_project_control()
    except Exception as exc:  # noqa: BLE001
        control = {}
        st.warning(
            f"Project control data could not be loaded: {exc}"
        )

    try:
        state = load_state()
    except Exception as exc:  # noqa: BLE001
        state = {}
        st.warning(
            f"Project state could not be loaded: {exc}"
        )

    try:
        events = load_events()
    except Exception as exc:  # noqa: BLE001
        events = []
        st.warning(
            f"Project events could not be loaded: {exc}"
        )

    try:
        git = git_info()
    except Exception as exc:  # noqa: BLE001
        git = {}
        st.warning(
            f"Git information could not be loaded: {exc}"
        )

    # =====================================================================
    # ROADMAP
    # =====================================================================

    steps = get_steps(
        control
    )

    progress = overall_progress(
        control,
        steps,
    )

    active_step = first_active_step(
        steps
    )

    # =====================================================================
    # PROJECT OVERVIEW
    # =====================================================================

    st.header(
        "⚔️ Project Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Project",
            "Einstein AI V2",
        )

    with col2:
        st.metric(
            "Overall Progress",
            f"{progress:.0f}%",
        )

    with col3:
        st.metric(
            "Roadmap Steps",
            str(len(steps)),
        )

    with col4:
        st.metric(
            "Events",
            str(len(events)),
        )

    st.progress(
        progress / 100.0
    )

    # =====================================================================
    # CURRENT STEP
    # =====================================================================

    st.header(
        "🔴 Current Mission"
    )

    if active_step:

        render_step_details(
            active_step
        )

    else:

        st.info(
            "No active roadmap step."
        )

    # =====================================================================
    # ROADMAP
    # =====================================================================

    st.header(
        "⚔️ Zanpakutō Roadmap"
    )

    if not steps:

        st.info(
            "No roadmap steps are currently available."
        )

    else:

        for index, step in enumerate(steps):

            if not isinstance(
                step,
                dict,
            ):
                continue

            with st.container():

                roadmap_card(
                    step,
                    index,
                )

    # =====================================================================
    # PROJECT STATE
    # =====================================================================

    st.header(
        "🜂 Project State"
    )

    if state:

        with st.expander(
            "Current Project State",
            expanded=False,
        ):

            for key, value in state.items():

                if isinstance(
                    value,
                    (dict, list),
                ):

                    st.write(
                        f"**{key}**"
                    )

                    st.json(
                        value
                    )

                else:

                    st.write(
                        f"**{key}:** {value}"
                    )

    else:

        st.info(
            "No project state is currently available."
        )

    # =====================================================================
    # RECENT EVENTS
    # =====================================================================

    st.header(
        "✨ Recent Reishi Events"
    )

    if events:

        recent_events = events[:10]

        for event in recent_events:

            if not isinstance(
                event,
                dict,
            ):
                continue

            timestamp = (
                event.get("timestamp")
                or event.get("time")
                or event.get("created_at")
                or ""
            )

            event_type = (
                event.get("event")
                or event.get("type")
                or event.get("action")
                or "EVENT"
            )

            message = (
                event.get("message")
                or event.get("description")
                or event.get("detail")
                or ""
            )

            with st.expander(
                f"{event_type} — {timestamp}",
                expanded=False,
            ):

                if message:
                    st.write(
                        message
                    )

                st.json(
                    event
                )

    else:

        st.info(
            "No project events are currently available."
        )

    # =====================================================================
    # GIT INFORMATION
    # =====================================================================

    st.header(
        "◆ Git Information"
    )

    if git:

        col1, col2 = st.columns(2)

        with col1:

            branch = (
                git.get("branch")
                or git.get("current_branch")
                or "Unknown"
            )

            st.metric(
                "Branch",
                str(branch),
            )

        with col2:

            commit = (
                git.get("commit")
                or git.get("sha")
                or git.get("commit_hash")
                or "Unknown"
            )

            commit_text = str(
                commit
            )

            if len(commit_text) > 12:
                commit_text = commit_text[:12]

            st.metric(
                "Commit",
                commit_text,
            )

        with st.expander(
            "Git Details",
            expanded=False,
        ):

            st.json(
                git
            )

    else:

        st.info(
            "Git information is not currently available."
        )

    # =====================================================================
    # SYSTEM STATUS
    # =====================================================================

    st.header(
        "⚡ System Status"
    )

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:

        st.success(
            "Streamlit UI active"
        )

    with status_col2:

        st.success(
            "Native rendering enabled"
        )

    with status_col3:

        st.success(
            "HTML UI disabled"
        )

    # =====================================================================
    # DATA SOURCE
    # =====================================================================

    with st.expander(
        "Dashboard Data Sources",
        expanded=False,
    ):

        st.write(
            "Project Control"
        )

        st.write(
            "Loaded through load_project_control()"
        )

        st.write(
            "Project State"
        )

        st.write(
            "Loaded through load_state()"
        )

        st.write(
            "Project Events"
        )

        st.write(
            "Loaded through load_events()"
        )

        st.write(
            "Git"
        )

        st.write(
            "Loaded through git_info()"
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    render_dashboard()
