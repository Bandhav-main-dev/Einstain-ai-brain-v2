from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"


def load_project_state() -> dict[str, Any]:
    """Load the current Einstein AI V2 project state."""
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_events() -> list[dict[str, Any]]:
    """Load project events from the JSONL event log."""
    if not EVENT_FILE.exists():
        return []

    events: list[dict[str, Any]] = []

    try:
        lines = EVENT_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return events

    for line in lines:
        if not line.strip():
            continue

        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return events


def get_git_value(*args: str) -> str:
    """Return a Git value without modifying the repository."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return "Unavailable"

    if result.returncode != 0:
        return "Unavailable"

    return result.stdout.strip() or "Unavailable"


def get_git_status() -> str:
    """Return the short Git status."""
    return get_git_value("status", "--short")


def get_recent_events(
    events: list[dict[str, Any]],
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Return the newest project events."""
    return list(reversed(events[-limit:]))


def inject_bleach_theme() -> None:
    """Inject the owner dashboard visual theme."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(52, 152, 219, 0.12),
                    transparent 35%
                ),
                radial-gradient(
                    circle at bottom left,
                    rgba(155, 89, 182, 0.10),
                    transparent 35%
                ),
                #07090d;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
        }

        .owner-title {
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-bottom: 0.1rem;
        }

        .owner-subtitle {
            color: #9aa4b2;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .dashboard-card {
            background: rgba(18, 22, 30, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow:
                0 8px 30px rgba(0, 0, 0, 0.25);
        }

        .card-label {
            color: #8f9aaa;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        .card-value {
            font-size: 1.55rem;
            font-weight: 700;
            margin-top: 0.35rem;
        }

        .status-running {
            color: #7dd3fc;
        }

        .status-complete {
            color: #86efac;
        }

        .status-warning {
            color: #facc15;
        }

        .status-error {
            color: #f87171;
        }

        .event-card {
            background: rgba(13, 17, 23, 0.92);
            border-left: 3px solid #6d5dfc;
            padding: 0.85rem 1rem;
            margin-bottom: 0.6rem;
            border-radius: 8px;
        }

        .event-time {
            color: #7f8a9a;
            font-size: 0.75rem;
        }

        .event-message {
            margin-top: 0.2rem;
            font-weight: 600;
        }

        .bleach-line {
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent,
                #ffffff,
                transparent
            );
            margin: 0.8rem 0 1.4rem 0;
            opacity: 0.45;
        }

        .small-muted {
            color: #7f8a9a;
            font-size: 0.82rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric(
    label: str,
    value: str,
    css_class: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="card-label">{label}</div>
            <div class="card-value {css_class}">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_event(event: dict[str, Any]) -> None:
    timestamp = (
        event.get("timestamp") or event.get("created_at") or event.get("time") or "Unknown time"
    )

    event_type = event.get("event_type") or event.get("type") or "EVENT"

    message = event.get("message") or event.get("description") or "Project event recorded."

    st.markdown(
        f"""
        <div class="event-card">
            <div class="event-time">
                {timestamp} · {event_type}
            </div>
            <div class="event-message">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    st.set_page_config(
        page_title="Einstein AI V2 — Owner Monitor",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_bleach_theme()

    state = load_project_state()
    events = load_events()

    progress = float(
        state.get(
            "overall_progress",
            state.get("progress_percent", 0.0),
        )
        or 0.0
    )

    current_phase = state.get(
        "current_phase",
        "Unknown",
    )

    current_step = state.get(
        "current_step",
        "Unknown",
    )

    project_status = state.get(
        "status",
        "UNKNOWN",
    )

    branch = get_git_value(
        "branch",
        "--show-current",
    )

    commit = get_git_value(
        "rev-parse",
        "--short",
        "HEAD",
    )

    git_status = get_git_status()

    st.markdown(
        '<div class="owner-title">⚔️ EINSTEIN AI V2 — OWNER MONITOR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="owner-subtitle">'
        "Private engineering command center · "
        "Monitoring project state, progress, events and tests"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="bleach-line"></div>',
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------

    with st.sidebar:
        st.header("⚔️ Owner Control")

        if st.button(
            "🔄 Refresh Dashboard",
            use_container_width=True,
        ):
            st.rerun()

        st.markdown("---")

        st.markdown("### Project")

        st.write("**Name:** Einstein AI V2")
        st.write(f"**Phase:** {current_phase}")
        st.write(f"**Step:** {current_step}")

        st.markdown("---")

        st.markdown("### Git")

        st.code(
            branch,
            language="text",
        )

        st.code(
            commit,
            language="text",
        )

        if git_status:
            st.warning("Working tree has changes.")
        else:
            st.success("Working tree clean.")

    # ------------------------------------------------------------
    # TOP METRICS
    # ------------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric(
            "Overall Progress",
            f"{progress:.1f}%",
        )

    with col2:
        status_class = (
            "status-running"
            if project_status == "RUNNING"
            else "status-complete"
            if project_status == "COMPLETE"
            else "status-warning"
        )

        render_metric(
            "Project Status",
            project_status,
            status_class,
        )

    with col3:
        render_metric(
            "Current Phase",
            str(current_phase),
        )

    with col4:
        render_metric(
            "Events Recorded",
            str(len(events)),
        )

    # ------------------------------------------------------------
    # PROGRESS
    # ------------------------------------------------------------

    st.markdown("## 📊 Engineering Progress")

    st.progress(min(max(progress / 100.0, 0.0), 1.0))

    st.caption(f"Current step: {current_step}")

    # ------------------------------------------------------------
    # PROJECT STATE
    # ------------------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.markdown("## 🧠 Project State")

        state_display = {
            "Version": state.get(
                "version",
                "Unknown",
            ),
            "Current phase": current_phase,
            "Current step": current_step,
            "Status": project_status,
            "Active branch": branch,
            "Current commit": commit,
            "Completed steps": state.get(
                "completed_steps",
                [],
            ),
            "Active steps": state.get(
                "active_steps",
                [],
            ),
        }

        st.json(state_display)

    with right:
        st.markdown("## 🧪 Testing")

        tests_passed = int(state.get("tests_passed", 0) or 0)

        tests_failed = int(state.get("tests_failed", 0) or 0)

        warnings = int(state.get("warnings", 0) or 0)

        errors = int(state.get("errors", 0) or 0)

        test_col1, test_col2 = st.columns(2)

        with test_col1:
            render_metric(
                "Tests Passed",
                str(tests_passed),
                "status-complete",
            )

            render_metric(
                "Warnings",
                str(warnings),
                "status-warning",
            )

        with test_col2:
            render_metric(
                "Tests Failed",
                str(tests_failed),
                ("status-error" if tests_failed else "status-complete"),
            )

            render_metric(
                "Errors",
                str(errors),
                ("status-error" if errors else "status-complete"),
            )

    # ------------------------------------------------------------
    # RECENT EVENTS
    # ------------------------------------------------------------

    st.markdown("## 📜 Recent Project Events")

    recent_events = get_recent_events(events)

    if not recent_events:
        st.info("No project events have been recorded yet.")
    else:
        for event in recent_events:
            render_event(event)

    # ------------------------------------------------------------
    # RAW LOG INSPECTION
    # ------------------------------------------------------------

    with st.expander(
        "🔍 Raw Project State",
        expanded=False,
    ):
        st.json(state)

    with st.expander(
        "📜 Raw Event Log",
        expanded=False,
    ):
        st.json(events)

    st.markdown(
        '<div class="small-muted">Einstein AI V2 Owner Monitoring System · Phase 0.6.4</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render_dashboard()
