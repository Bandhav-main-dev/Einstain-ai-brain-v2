"""
Einstein AI V2 — Owner Zanpakutō Command Center.

OWNER COMMAND CENTER
SYSTEM TELEMETRY

The dashboard is intentionally owner-focused:
- What is complete?
- What is currently being built?
- What remains?
- What is the next mission?
- What does each project step contain?

Project control is stored in monitor/project_control.json.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

# OWNER COMMAND CENTER
# SYSTEM TELEMETRY

OWNER_FILE = Path(__file__).resolve()
PROJECT_ROOT = OWNER_FILE.parents[1]

STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"
CONTROL_FILE = OWNER_FILE.parent / "project_control.json"


def load_state() -> dict[str, Any]:
    """Load project state safely."""
    if not STATE_FILE.exists():
        return {}

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def load_events() -> list[dict[str, Any]]:
    """Load project events, newest first."""
    if not EVENT_FILE.exists():
        return []

    events: list[dict[str, Any]] = []

    try:
        lines = EVENT_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(item, dict):
            events.append(item)

    return list(reversed(events))


def load_project_control() -> dict[str, Any]:
    """Load the owner project-control JSON."""
    if not CONTROL_FILE.exists():
        return {}

    try:
        data = json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def git_info() -> dict[str, str]:
    """Return basic repository information."""
    def run_git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    return {
        "branch": run_git("branch", "--show-current") or "unknown",
        "commit": run_git("rev-parse", "--short", "HEAD") or "unknown",
        "status": run_git("status", "--short"),
    }


def inject_theme() -> None:
    """Inject the compact red/black/white/gold Zanpakutō theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(170,0,0,.20), transparent 25%),
                radial-gradient(circle at 90% 20%, rgba(212,175,55,.10), transparent 22%),
                linear-gradient(135deg, #050505 0%, #0b0b0b 55%, #160000 100%);
            color: #f5f5f5;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: 'Cinzel', serif !important;
            letter-spacing: .04em;
        }

        .hero {
            border: 1px solid rgba(212,175,55,.45);
            border-left: 5px solid #a40000;
            background: linear-gradient(135deg, rgba(20,20,20,.96), rgba(55,0,0,.72));
            padding: 18px 22px;
            border-radius: 10px;
            box-shadow: 0 0 28px rgba(164,0,0,.18);
            margin-bottom: 14px;
        }

        .hero-title {
            color: #ffffff;
            font-family: 'Cinzel', serif;
            font-size: 27px;
            font-weight: 700;
        }

        .hero-sub {
            color: #d7d7d7;
            font-size: 13px;
            margin-top: 4px;
        }

        .gold {
            color: #d4af37;
        }

        .telemetry-card,
        .mission-card,
        .roadmap-card,
        .event-card {
            border-radius: 9px;
            padding: 12px 14px;
            background: rgba(15,15,15,.90);
            border: 1px solid rgba(255,255,255,.10);
            margin-bottom: 8px;
        }

        .telemetry-card {
            border-top: 2px solid #d4af37;
        }

        .mission-card {
            border-left: 4px solid #a40000;
            background: linear-gradient(90deg, rgba(95,0,0,.35), rgba(10,10,10,.94));
        }

        .roadmap-card {
            border-left: 3px solid #d4af37;
        }

        .event-card {
            border-left: 3px solid #ffffff;
        }

        .step-title {
            font-weight: 700;
            font-size: 15px;
        }

        .step-meta {
            color: #bdbdbd;
            font-size: 12px;
        }

        .small {
            font-size: 12px;
            color: #c5c5c5;
        }

        .reiatsu-flow {
            height: 3px;
            margin: 10px 0 14px;
            background: linear-gradient(90deg, #8d0000, #d4af37, #ffffff, #8d0000);
            background-size: 300% 100%;
            animation: reiatsu 5s linear infinite;
            border-radius: 5px;
        }

        @keyframes reiatsu {
            0% { background-position: 0% 50%; }
            100% { background-position: 300% 50%; }
        }

        .status-completed { color: #d4af37; }
        .status-progress { color: #ffffff; }
        .status-planned { color: #999999; }

        div[data-testid="stMetricValue"] {
            font-size: 24px;
        }

        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, #8d0000, #d4af37);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_icon(status: str) -> str:
    return {
        "completed": "⚔️",
        "in_progress": "🔥",
        "planned": "○",
    }.get(status, "◆")


def render_header(control: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">⚔️ ZANPAKUTŌ COMMAND CENTER</div>
            <div class="hero-sub">
                <span class="gold">EINSTEIN AI V2</span>
                &nbsp;•&nbsp; Owner Project Control
                &nbsp;•&nbsp; {control.get("status", "UNKNOWN")}
            </div>
        </div>
        <div class="reiatsu-flow"></div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(control: dict[str, Any]) -> None:
    steps = control.get("steps", [])
    completed = sum(1 for s in steps if s.get("status") == "completed")
    active = sum(1 for s in steps if s.get("status") == "in_progress")
    planned = sum(1 for s in steps if s.get("status") == "planned")

    progress = float(control.get("overall_progress", 0))

    a, b, c, d = st.columns(4)

    with a:
        st.metric("PROJECT", control.get("project", "Einstein AI V2"))

    with b:
        st.metric("PROGRESS", f"{progress:.0f}%")

    with c:
        st.metric("COMPLETED", completed)

    with d:
        st.metric("REMAINING", active + planned)

    st.progress(min(max(progress / 100, 0), 1))


def render_next_mission(control: dict[str, Any]) -> None:
    st.subheader("NEXT MISSION")

    current = next(
        (
            step
            for step in control.get("steps", [])
            if step.get("status") == "in_progress"
        ),
        None,
    )

    if current:
        st.markdown(
            f"""
            <div class="mission-card">
                <div class="step-title">
                    {status_icon(current.get("status", ""))}
                    {current.get("id", "")} — {current.get("name", "")}
                </div>
                <div class="small">
                    {current.get("summary", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        actions = current.get("next_actions", [])
        if actions:
            st.markdown("**Immediate actions**")
            for action in actions:
                st.markdown(f"- {action}")

    mission = control.get("next_mission")
    if mission:
        st.info(mission)


def render_roadmap(control: dict[str, Any]) -> None:
    st.subheader("PROJECT ROADMAP")

    steps = control.get("steps", [])

    for step in steps:
        status = step.get("status", "planned")
        progress = float(step.get("progress", 0))

        with st.expander(
            f"{status_icon(status)} {step.get('id', '')} — "
            f"{step.get('name', '')}   [{progress:.0f}%]"
        ):
            st.markdown(
                f"""
                <div class="roadmap-card">
                    <div class="step-title">{step.get("name", "")}</div>
                    <div class="step-meta">
                        Status: {status.replace("_", " ").upper()}
                    </div>
                    <p>{step.get("summary", "")}</p>
                    <p><b>What this step does:</b> {step.get("what_it_does", "")}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.progress(min(max(progress / 100, 0), 1))

            completed = step.get("completed", [])
            remaining = step.get("remaining", [])
            actions = step.get("next_actions", [])
            deliverables = step.get("deliverables", [])
            dependencies = step.get("dependencies", [])

            left, right = st.columns(2)

            with left:
                st.markdown("**Completed**")
                if completed:
                    for item in completed:
                        st.markdown(f"- ✅ {item}")
                else:
                    st.markdown("- None recorded yet")

                st.markdown("**Remaining**")
                if remaining:
                    for item in remaining:
                        st.markdown(f"- ⏳ {item}")
                else:
                    st.markdown("- None")

            with right:
                st.markdown("**Next actions**")
                if actions:
                    for item in actions:
                        st.markdown(f"- ▶️ {item}")
                else:
                    st.markdown("- None")

                st.markdown("**Deliverables**")
                if deliverables:
                    for item in deliverables:
                        st.markdown(f"- 📦 `{item}`")

                if dependencies:
                    st.markdown("**Depends on**")
                    st.caption(" • ".join(dependencies))


def render_work_summary(control: dict[str, Any]) -> None:
    st.subheader("WORK STATUS")

    completed = [
        s for s in control.get("steps", [])
        if s.get("status") == "completed"
    ]

    remaining = [
        s for s in control.get("steps", [])
        if s.get("status") != "completed"
    ]

    left, right = st.columns(2)

    with left:
        st.markdown("### ✅ COMPLETED WORK")
        for step in completed:
            st.markdown(
                f"""
                <div class="roadmap-card">
                    <b>{step.get("id")} — {step.get("name")}</b><br>
                    <span class="small">{step.get("summary", "")}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("### ⏳ REMAINING WORK")
        for step in remaining:
            st.markdown(
                f"""
                <div class="mission-card">
                    <b>{step.get("id")} — {step.get("name")}</b><br>
                    <span class="small">
                        {step.get("progress", 0)}% complete
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_events(events: list[dict[str, Any]]) -> None:
    st.subheader("PROJECT EVENTS")

    if not events:
        st.caption("No project events recorded yet.")
        return

    for event in events[:12]:
        event_type = event.get("event_type", "EVENT")
        message = event.get("message", "")
        timestamp = event.get("timestamp", event.get("time", ""))

        st.markdown(
            f"""
            <div class="event-card">
                <b>{event_type}</b>
                <span class="small"> {timestamp}</span><br>
                {message}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_project_information(control: dict[str, Any]) -> None:
    st.subheader("PROJECT INFORMATION")

    left, right = st.columns(2)

    with left:
        st.markdown(f"**Project:** {control.get('project', 'Einstein AI V2')}")
        st.markdown(f"**Version:** {control.get('version', '2.0')}")
        st.markdown(f"**Status:** {control.get('status', 'UNKNOWN')}")

    with right:
        st.markdown(
            f"**Current step:** {control.get('current_step', 'Unknown')}"
        )
        st.markdown(
            f"**Last updated:** {control.get('last_updated', 'Unknown')}"
        )


def render_system_telemetry(state: dict[str, Any], git: dict[str, str]) -> None:
    st.subheader("SYSTEM TELEMETRY")

    a, b, c = st.columns(3)

    with a:
        st.markdown(
            f"""
            <div class="telemetry-card">
                <b>Git Branch</b><br>
                {git.get("branch", "unknown")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b:
        st.markdown(
            f"""
            <div class="telemetry-card">
                <b>Commit</b><br>
                {git.get("commit", "unknown")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c:
        phase = state.get("current_phase", "Owner Control Center")
        st.markdown(
            f"""
            <div class="telemetry-card">
                <b>Active Phase</b><br>
                {phase}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ⚔️ OWNER")
        st.caption("Zanpakutō Project Control")

        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.markdown("### Control Sources")
        st.caption("project_control.json")
        st.caption("project_state.json")
        st.caption("project_events.jsonl")

        st.markdown("---")
        st.markdown("### Mission Philosophy")
        st.caption("PLAN")
        st.caption("BUILD")
        st.caption("VALIDATE")
        st.caption("LEARN")
        st.caption("ADVANCE")


def render_dashboard() -> None:
    st.set_page_config(
        page_title="Einstein AI V2 — Zanpakutō Command Center",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_theme()
    render_sidebar()

    control = load_project_control()
    state = load_state()
    events = load_events()
    git = git_info()

    if not control:
        st.error("Project control data could not be loaded.")
        st.stop()

    render_header(control)
    render_overview(control)
    render_next_mission(control)

    st.markdown("---")
    render_roadmap(control)

    st.markdown("---")
    render_work_summary(control)

    st.markdown("---")
    render_events(events)

    st.markdown("---")
    render_project_information(control)

    st.markdown("---")
    render_system_telemetry(state, git)

    st.markdown(
        """
        <div style="text-align:center; padding:16px; color:#777;">
            ⚔️ EINSTEIN AI V2 &nbsp;•&nbsp;
            OWNER COMMAND CENTER &nbsp;•&nbsp;
            <span style="color:#d4af37;">PLAN • BUILD • LEARN • ADVANCE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render_dashboard()
