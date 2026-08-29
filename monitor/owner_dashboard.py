"""
Einstein AI V2 — Owner Zanpakutō Command Center.

The dashboard is intentionally owner-focused.

Project roadmap and mission data are loaded from:
    monitor/project_control.json

The Owner UI does not expose developer-only validation controls.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

# OWNER COMMAND CENTER
# ZANPAKUTŌ COMMAND CENTER
# SYSTEM TELEMETRY
# PROJECT EVENTS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONITOR_DIR = PROJECT_ROOT / "monitor"

OWNER_FILE = Path(__file__)
CONTROL_FILE = MONITOR_DIR / "project_control.json"
STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"


def load_state() -> dict[str, Any]:
    """Load project state while remaining compatible with tests."""
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
    """Load the owner project-control source of truth."""
    if not CONTROL_FILE.exists():
        return {}

    try:
        data = json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def git_info() -> dict[str, str]:
    """Return lightweight Git information."""
    def run_git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() or "unknown"

    return {
        "branch": run_git("branch", "--show-current"),
        "commit": run_git("rev-parse", "--short", "HEAD"),
        "status": run_git("status", "--short", "--branch"),
    }


def inject_theme() -> None:
    """Inject compact Zanpakutō-inspired styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        :root {
            --red: #b11226;
            --dark-red: #7d0b19;
            --black: #070707;
            --black2: #111111;
            --white: #f4f1ea;
            --gold: #d4af37;
            --muted: #a7a7a7;
            --line: rgba(212,175,55,.28);
        }

        .stApp {
            background:
                radial-gradient(circle at 80% 8%, rgba(177,18,38,.18), transparent 27%),
                radial-gradient(circle at 12% 30%, rgba(212,175,55,.08), transparent 25%),
                linear-gradient(135deg, #050505 0%, #0c0c0c 48%, #100407 100%);
            color: var(--white);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: "Cinzel", serif !important;
            letter-spacing: .04em;
        }

        .hero {
            border: 1px solid var(--line);
            border-left: 5px solid var(--red);
            background: linear-gradient(100deg, rgba(177,18,38,.16), rgba(10,10,10,.88));
            padding: 18px 22px;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(177,18,38,.12);
            margin-bottom: 14px;
        }

        .hero-title {
            color: var(--white);
            font-family: "Cinzel", serif;
            font-size: 25px;
            font-weight: 700;
        }

        .hero-sub {
            color: #bcbcbc;
            font-size: 12px;
            margin-top: 4px;
        }

        .section {
            color: var(--gold);
            font-family: "Cinzel", serif;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: .08em;
            border-bottom: 1px solid var(--line);
            padding-bottom: 5px;
            margin: 18px 0 10px;
        }

        .card {
            background: linear-gradient(145deg, rgba(18,18,18,.96), rgba(8,8,8,.96));
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 10px;
            padding: 13px 15px;
            margin-bottom: 9px;
            min-height: 80px;
        }

        .card:hover {
            border-color: rgba(212,175,55,.42);
            box-shadow: 0 0 18px rgba(212,175,55,.07);
        }

        .telemetry-card {
            background: #0b0b0b;
            border: 1px solid rgba(212,175,55,.20);
            border-top: 3px solid var(--gold);
            border-radius: 9px;
            padding: 11px;
            text-align: center;
        }

        .telemetry-value {
            color: var(--gold);
            font-family: "Cinzel", serif;
            font-size: 21px;
            font-weight: 700;
        }

        .telemetry-label {
            color: #aaa;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .08em;
        }

        .mission-card {
            border: 1px solid rgba(177,18,38,.60);
            border-left: 4px solid var(--red);
            background: linear-gradient(110deg, rgba(177,18,38,.16), #0b0b0b);
            border-radius: 10px;
            padding: 15px;
        }

        .mission-title {
            font-family: "Cinzel", serif;
            color: var(--white);
            font-size: 18px;
            font-weight: 700;
        }

        .roadmap-card {
            border: 1px solid rgba(255,255,255,.08);
            background: #0b0b0b;
            border-radius: 9px;
            padding: 12px;
            margin-bottom: 8px;
        }

        .roadmap-card.active {
            border-color: rgba(177,18,38,.72);
            box-shadow: inset 4px 0 0 var(--red);
        }

        .roadmap-card.completed {
            border-color: rgba(212,175,55,.20);
        }

        .roadmap-name {
            font-family: "Cinzel", serif;
            font-weight: 700;
            color: var(--white);
        }

        .roadmap-meta {
            color: #999;
            font-size: 11px;
        }

        .progress-shell {
            background: #1a1a1a;
            border-radius: 20px;
            height: 7px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-fill {
            background: linear-gradient(90deg, var(--red), var(--gold));
            height: 100%;
            border-radius: 20px;
        }

        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: .06em;
            text-transform: uppercase;
            margin-right: 5px;
        }

        .badge-completed {
            background: rgba(212,175,55,.14);
            color: var(--gold);
        }

        .badge-active {
            background: rgba(177,18,38,.18);
            color: #ff6375;
        }

        .badge-planned {
            background: rgba(255,255,255,.07);
            color: #aaa;
        }

        .event-card {
            border-left: 3px solid var(--gold);
            background: #0b0b0b;
            padding: 9px 12px;
            border-radius: 7px;
            margin-bottom: 7px;
            font-size: 12px;
        }

        .detail-title {
            color: var(--gold);
            font-family: "Cinzel", serif;
            font-size: 13px;
            font-weight: 700;
            margin-top: 7px;
        }

        .detail-text {
            color: #c6c6c6;
            font-size: 12px;
            line-height: 1.5;
        }

        .reiatsu-flow {
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent,
                var(--red),
                var(--gold),
                var(--red),
                transparent
            );
            animation: reiatsu 3s ease-in-out infinite;
            margin: 8px 0 14px;
        }

        @keyframes reiatsu {
            0%, 100% { opacity: .35; transform: scaleX(.75); }
            50% { opacity: 1; transform: scaleX(1); }
        }

        .footer {
            color: #666;
            text-align: center;
            font-size: 10px;
            padding-top: 18px;
            letter-spacing: .08em;
        }

        [data-testid="stSidebar"] {
            background: #090909;
            border-right: 1px solid rgba(212,175,55,.18);
        }

        [data-testid="stMetricValue"] {
            color: var(--gold);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    normalized = status.lower().strip()
    if normalized == "completed":
        return '<span class="badge badge-completed">COMPLETED</span>'
    if normalized == "active":
        return '<span class="badge badge-active">ACTIVE</span>'
    return f'<span class="badge badge-planned">{normalized.upper()}</span>'


def render_hero(project: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">⚔ ZANPAKUTŌ COMMAND CENTER</div>
            <div class="hero-sub">
                OWNER COMMAND CENTER · {project.get("name", "Einstein AI V2")}
            </div>
        </div>
        <div class="reiatsu-flow"></div>
        """,
        unsafe_allow_html=True,
    )


def render_telemetry(project: dict[str, Any], roadmap: list[dict[str, Any]]) -> None:
    completed = sum(item.get("status") == "completed" for item in roadmap)
    active = sum(item.get("status") == "active" for item in roadmap)
    planned = sum(item.get("status") == "planned" for item in roadmap)

    cols = st.columns(5)

    values = [
        (f"{project.get('overall_progress', 0)}%", "OVERALL"),
        (str(completed), "COMPLETED"),
        (str(active), "ACTIVE"),
        (str(planned), "PLANNED"),
        (project.get("health", "UNKNOWN"), "HEALTH"),
    ]

    for col, (value, label) in zip(cols, values):
        with col:
            st.markdown(
                f"""
                <div class="telemetry-card">
                    <div class="telemetry-value">{value}</div>
                    <div class="telemetry-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_mission(mission: dict[str, Any]) -> None:
    st.markdown('<div class="section">⚔ NEXT MISSION</div>', unsafe_allow_html=True)

    tasks = mission.get("tasks", [])
    expected = mission.get("expected_output", [])

    task_html = "".join(f"<li>{task}</li>" for task in tasks)
    output_html = "".join(f"<li>{item}</li>" for item in expected)

    st.markdown(
        f"""
        <div class="mission-card">
            <div class="mission-title">
                {mission.get("id", "MISSION")} · {mission.get("title", "No mission")}
            </div>
            <div class="detail-text" style="margin-top:7px;">
                {mission.get("objective", "")}
            </div>

            <div class="detail-title">WHY THIS MATTERS</div>
            <div class="detail-text">{mission.get("why", "")}</div>

            <div class="detail-title">MISSION TASKS</div>
            <ul class="detail-text">{task_html}</ul>

            <div class="detail-title">EXPECTED OUTPUT</div>
            <ul class="detail-text">{output_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_roadmap(roadmap: list[dict[str, Any]]) -> None:
    st.markdown('<div class="section">PROJECT ROADMAP</div>', unsafe_allow_html=True)

    for step in roadmap:
        status = step.get("status", "planned")
        progress = max(0, min(100, int(step.get("progress", 0))))

        css_class = "active" if status == "active" else (
            "completed" if status == "completed" else ""
        )

        st.markdown(
            f"""
            <div class="roadmap-card {css_class}">
                <div>
                    <span class="roadmap-name">
                        {step.get("id", "?")} · {step.get("name", "Unnamed")}
                    </span>
                    {status_badge(status)}
                </div>

                <div class="roadmap-meta">
                    Priority: {step.get("priority", "normal").upper()}
                    · Progress: {progress}%
                </div>

                <div class="progress-shell">
                    <div class="progress-fill" style="width:{progress}%"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"View details · {step.get('id', '?')} · {step.get('name', 'Step')}",
            expanded=(status == "active"),
        ):
            st.markdown(
                f"**Purpose:** {step.get('summary', '')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Completed**")
                done = step.get("what_done", [])
                if done:
                    for item in done:
                        st.markdown(f"✅ {item}")
                else:
                    st.caption("No completed work recorded.")

                st.markdown("**Remaining**")
                remaining = step.get("remaining", [])
                if remaining:
                    for item in remaining:
                        st.markdown(f"⬜ {item}")
                else:
                    st.caption("No remaining work recorded.")

            with col2:
                st.markdown("**Plan**")
                for item in step.get("plan", []):
                    st.markdown(f"→ {item}")

                st.markdown("**Deliverables**")
                for item in step.get("deliverables", []):
                    st.markdown(f"📦 {item}")

                st.markdown("**Dependencies**")
                dependencies = step.get("dependencies", [])
                if dependencies:
                    for item in dependencies:
                        st.markdown(f"🔗 {item}")
                else:
                    st.caption("None")

            st.markdown(
                f"""
                <div class="card">
                    <div class="detail-title">NEXT ACTION</div>
                    <div class="detail-text">
                        {step.get("next_action", "No next action recorded.")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_work_summary(roadmap: list[dict[str, Any]]) -> None:
    completed = [x for x in roadmap if x.get("status") == "completed"]
    active = [x for x in roadmap if x.get("status") == "active"]
    remaining = [
        x for x in roadmap
        if x.get("status") in {"planned", "blocked", "locked"}
    ]

    st.markdown('<div class="section">WORK SUMMARY</div>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown("### COMPLETED WORK")
        if completed:
            for item in completed:
                st.markdown(
                    f"""
                    <div class="card">
                        {status_badge("completed")}
                        <b>{item.get("id")} · {item.get("name")}</b>
                        <div class="detail-text">
                            {item.get("summary", "")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No completed work recorded.")

    with right:
        st.markdown("### REMAINING WORK")
        if active:
            for item in active:
                st.markdown(
                    f"""
                    <div class="card">
                        {status_badge("active")}
                        <b>{item.get("id")} · {item.get("name")}</b>
                        <div class="detail-text">
                            {item.get("summary", "")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        for item in remaining:
            st.markdown(
                f"""
                <div class="card">
                    {status_badge(item.get("status", "planned"))}
                    <b>{item.get("id")} · {item.get("name")}</b>
                    <div class="detail-text">
                        {item.get("summary", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_events(events: list[dict[str, Any]]) -> None:
    st.markdown('<div class="section">PROJECT EVENTS</div>', unsafe_allow_html=True)

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
                <span style="color:#777;"> {timestamp}</span>
                <div>{message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_project_information(
    project: dict[str, Any],
    git: dict[str, str],
    notes: list[str],
) -> None:
    st.markdown(
        '<div class="section">PROJECT INFORMATION</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.markdown(
            f"""
            <div class="card">
                <div class="detail-title">PROJECT</div>
                <div class="detail-text">{project.get("name", "")}</div>

                <div class="detail-title">CODENAME</div>
                <div class="detail-text">{project.get("codename", "")}</div>

                <div class="detail-title">CURRENT PHASE</div>
                <div class="detail-text">{project.get("current_phase", "")}</div>

                <div class="detail-title">HEALTH</div>
                <div class="detail-text">{project.get("health", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="card">
                <div class="detail-title">BRANCH</div>
                <div class="detail-text">{git.get("branch", "unknown")}</div>

                <div class="detail-title">COMMIT</div>
                <div class="detail-text">{git.get("commit", "unknown")}</div>

                <div class="detail-title">OWNER NOTES</div>
                <div class="detail-text">
                    {"<br>".join(notes)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard() -> None:
    st.set_page_config(
        page_title="Einstein AI V2 — Zanpakutō Command Center",
        page_icon="⚔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_theme()

    control = load_project_control()

    if not control:
        st.error("Project control data could not be loaded.")
        return

    project = control.get("project", {})
    roadmap = control.get("roadmap", [])
    mission = control.get("current_mission", {})
    notes = control.get("owner_notes", [])

    render_hero(project)
    render_telemetry(project, roadmap)

    render_mission(mission)
    render_work_summary(roadmap)

    render_roadmap(roadmap)

    events = load_events()
    render_events(events)

    git = git_info()
    render_project_information(project, git, notes)

    st.markdown(
        """
        <div class="footer">
            EINSTEIN AI V2 · OWNER CONTROL CENTER ·
            PLAN • BUILD • VALIDATE • ADVANCE
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render_dashboard()
