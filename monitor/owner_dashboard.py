from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st

from .auth import login_form, logout, require_role

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"


def load_state() -> dict[str, Any]:
    """Load current Einstein AI V2 project state."""
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_events(limit: int = 20) -> list[dict[str, Any]]:
    """Load the most recent monitoring events."""
    if not EVENT_FILE.exists():
        return []

    events: list[dict[str, Any]] = []

    try:
        lines = EVENT_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    for line in lines[-limit:]:
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                events.append(value)
        except json.JSONDecodeError:
            continue

    return list(reversed(events))


def git_info() -> dict[str, str]:
    """Return safe read-only Git information."""

    def command(args: list[str]) -> str:
        try:
            result = subprocess.run(
                args,
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            return result.stdout.strip()
        except OSError:
            return ""

    return {
        "branch": command(["git", "branch", "--show-current"]),
        "commit": command(["git", "rev-parse", "--short", "HEAD"]),
        "status": command(["git", "status", "--short"]),
    }


def inject_theme() -> None:
    """Inject the Soul-Society-inspired dashboard theme."""

    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700'
            '&family=Rajdhani:wght@400;500;600;700&display=swap'
        );

        :root {
            --ink: #05070c;
            --night: #080d16;
            --panel: rgba(12, 18, 30, 0.88);
            --panel2: rgba(18, 27, 43, 0.82);
            --line: rgba(190, 205, 230, 0.16);
            --white: #edf3ff;
            --muted: #91a0b8;
            --spirit: #bcd7ff;
            --ice: #78bfff;
            --danger: #ff758f;
            --success: #72e6a5;
            --gold: #e9c978;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 12% 15%,
                    rgba(76, 136, 255, 0.15),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 88% 20%,
                    rgba(176, 211, 255, 0.09),
                    transparent 25%
                ),
                linear-gradient(
                    135deg,
                    #03050a 0%,
                    #07101d 48%,
                    #03060c 100%
                );
            color: var(--white);
            font-family: 'Rajdhani', sans-serif;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(
                    120deg,
                    transparent 0%,
                    rgba(255,255,255,0.025) 50%,
                    transparent 100%
                );
            animation: spiritSweep 9s linear infinite;
            z-index: 0;
        }

        @keyframes spiritSweep {
            0% {
                transform: translateX(-40%);
                opacity: 0.15;
            }
            50% {
                opacity: 0.35;
            }
            100% {
                transform: translateX(40%);
                opacity: 0.15;
            }
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 28px 34px;
            background:
                linear-gradient(
                    135deg,
                    rgba(16, 27, 45, 0.95),
                    rgba(7, 12, 22, 0.92)
                );
            box-shadow:
                0 25px 80px rgba(0, 0, 0, 0.45),
                inset 0 1px 0 rgba(255,255,255,0.06);
            margin-bottom: 20px;
        }

        .hero::after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            right: -120px;
            top: -120px;
            border-radius: 50%;
            border: 1px solid rgba(120,191,255,0.18);
            box-shadow:
                0 0 40px rgba(120,191,255,0.08),
                0 0 100px rgba(120,191,255,0.04);
            animation: pulseRing 4s ease-in-out infinite;
        }

        @keyframes pulseRing {
            0%, 100% {
                transform: scale(0.92);
                opacity: 0.45;
            }
            50% {
                transform: scale(1.08);
                opacity: 0.9;
            }
        }

        .hero-kicker {
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: 0.28em;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .hero-title {
            font-family: 'Cinzel', serif;
            font-size: clamp(2rem, 4vw, 4.2rem);
            line-height: 1;
            margin: 10px 0;
            color: var(--white);
            text-shadow:
                0 0 18px rgba(160, 204, 255, 0.22);
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 1.05rem;
        }

        .status-pill {
            display: inline-block;
            padding: 7px 14px;
            border-radius: 999px;
            background: rgba(114, 230, 165, 0.09);
            border: 1px solid rgba(114, 230, 165, 0.28);
            color: var(--success);
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .section-title {
            font-family: 'Cinzel', serif;
            color: var(--spirit);
            letter-spacing: 0.08em;
            font-size: 1.15rem;
            margin: 18px 0 12px;
        }

        .metric-card {
            border: 1px solid var(--line);
            border-radius: 17px;
            padding: 18px;
            min-height: 118px;
            background: linear-gradient(
                145deg,
                rgba(20, 31, 49, 0.86),
                rgba(7, 12, 22, 0.88)
            );
            transition:
                transform 0.25s ease,
                border-color 0.25s ease,
                box-shadow 0.25s ease;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(120,191,255,0.36);
            box-shadow: 0 15px 45px rgba(0,0,0,0.28);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }

        .metric-value {
            font-family: 'Cinzel', serif;
            color: var(--white);
            font-size: 2rem;
            margin-top: 7px;
        }

        .metric-detail {
            color: var(--muted);
            font-size: 0.85rem;
        }

        .panel {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 20px;
            background: var(--panel);
            box-shadow: 0 18px 55px rgba(0,0,0,0.22);
        }

        .event {
            border-left: 2px solid rgba(120,191,255,0.4);
            padding: 10px 14px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.025);
            border-radius: 0 10px 10px 0;
        }

        .event-type {
            color: var(--ice);
            font-weight: 700;
            font-size: 0.8rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .event-message {
            color: var(--white);
            margin-top: 3px;
        }

        .event-time {
            color: var(--muted);
            font-size: 0.75rem;
        }

        .timeline-item {
            position: relative;
            padding: 13px 16px 13px 28px;
            border-left: 1px solid rgba(120,191,255,0.22);
            margin-left: 8px;
        }

        .timeline-item::before {
            content: "";
            position: absolute;
            left: -5px;
            top: 17px;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: var(--ice);
            box-shadow: 0 0 15px rgba(120,191,255,0.55);
        }

        .timeline-complete::before {
            background: var(--success);
            box-shadow: 0 0 15px rgba(114,230,165,0.55);
        }

        .stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(120,191,255,0.28);
            background: rgba(120,191,255,0.07);
            color: var(--white);
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            border-color: rgba(120,191,255,0.55);
            box-shadow: 0 10px 28px rgba(0,0,0,0.25);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    rgba(5, 9, 17, 0.98),
                    rgba(8, 15, 26, 0.98)
                );
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-family: 'Cinzel', serif;
        }

        .small-note {
            color: var(--muted);
            font-size: 0.82rem;
        }

        .danger {
            color: var(--danger);
        }

        .success {
            color: var(--success);
        }

        .gold {
            color: var(--gold);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(
    label: str,
    value: str,
    detail: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_events(events: list[dict[str, Any]]) -> None:
    if not events:
        st.markdown(
            '<div class="small-note">No monitoring events recorded.</div>',
            unsafe_allow_html=True,
        )
        return

    for event in events:
        event_type = str(
            event.get("event_type")
            or event.get("type")
            or "event"
        )

        message = str(
            event.get("message")
            or event.get("description")
            or "Monitoring event"
        )

        timestamp = str(
            event.get("timestamp")
            or event.get("created_at")
            or ""
        )

        st.markdown(
            f"""
            <div class="event">
                <div class="event-type">{event_type}</div>
                <div class="event-message">{message}</div>
                <div class="event-time">{timestamp}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_timeline(state: dict[str, Any]) -> None:
    completed = state.get("completed_steps", [])
    active = state.get("active_steps", [])

    items = [
        ("0.6.1", "Monitoring Core", "Monitoring logging foundation"),
        ("0.6.2", "Project State + Schema", "State and event contracts"),
        ("0.6.3", "Progress Engine", "Progress calculation engine"),
        ("0.6.4", "Owner Dashboard", "Owner monitoring interface"),
        ("0.6.5", "Professor + Authentication", "Secure professor/test access"),
        ("0.6.4-U1", "UI Overhaul", "Landscape Soul-Society-inspired interface"),
    ]

    for phase, title, description in items:
        if phase in completed:
            css = "timeline-item timeline-complete"
            state_text = "COMPLETE"
        elif phase in active:
            css = "timeline-item"
            state_text = "ACTIVE"
        else:
            css = "timeline-item"
            state_text = "PLANNED"

        st.markdown(
            f"""
            <div class="{css}">
                <strong>{phase} — {title}</strong>
                <div class="small-note">
                    {state_text} · {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="Einstein AI V2 — Owner Command Center",
        page_icon="⚔",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_theme()

    if not login_form():
        return

    if not require_role("owner"):
        st.error("Owner role required.")
        return

    state = load_state()
    events = load_events()
    git = git_info()

    progress = state.get(
        "overall_progress",
        state.get("progress_percent", 0.0),
    )

    try:
        progress = float(progress)
    except (TypeError, ValueError):
        progress = 0.0

    progress = max(0.0, min(100.0, progress))

    status = str(state.get("status", "UNKNOWN"))
    phase = str(state.get("current_phase", "N/A"))
    step = str(state.get("current_step", "N/A"))
    tests_passed = int(state.get("tests_passed", 0) or 0)
    tests_failed = int(state.get("tests_failed", 0) or 0)
    warnings = int(state.get("warnings", 0) or 0)
    errors = int(state.get("errors", 0) or 0)

    # ------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------

    with st.sidebar:
        st.markdown(
            """
            <div class="section-title">OWNER CONTROL</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="status-pill">● COMMAND CENTER ONLINE</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("↻ Refresh Dashboard", use_container_width=True):
            st.rerun()

        if st.button("⟳ Rerun Test Suite", use_container_width=True):
            st.session_state["request_test_run"] = True
            st.rerun()

        st.markdown("---")

        st.markdown("### Project")
        st.write("Einstein AI V2")

        st.markdown("### Branch")
        st.code(git["branch"] or "unknown")

        st.markdown("### Commit")
        st.code(git["commit"] or "unknown")

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

        st.markdown(
            """
            <div class="small-note">
                Owner-level monitoring controls.<br>
                Read-only project telemetry unless explicitly enabled
                by the monitoring layer.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # HERO
    # ------------------------------------------------------------------

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">
                Einstein AI V2 · Monitoring Division
            </div>

            <div class="hero-title">
                OWNER COMMAND CENTER
            </div>

            <div class="hero-subtitle">
                A high-visibility monitoring interface for the AI research
                system — inspired by a Soul-Society command architecture.
            </div>

            <div style="margin-top:18px;">
                <span class="status-pill">
                    ● {status}
                </span>
                <span style="margin-left:12px;color:#91a0b8;">
                    Phase {phase} · {step}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # TOP METRICS
    # ------------------------------------------------------------------

    st.markdown(
        '<div class="section-title">SYSTEM TELEMETRY</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(6)

    with columns[0]:
        metric_card("Overall Progress", f"{progress:.1f}%", "Research path")

    with columns[1]:
        metric_card("Current Phase", phase, "Active phase")

    with columns[2]:
        metric_card("Tests Passed", str(tests_passed), "Validation")

    with columns[3]:
        metric_card("Tests Failed", str(tests_failed), "Validation")

    with columns[4]:
        metric_card("Warnings", str(warnings), "Monitoring")

    with columns[5]:
        metric_card("Errors", str(errors), "Critical")

    st.write("")

    # ------------------------------------------------------------------
    # PROGRESS
    # ------------------------------------------------------------------

    left, right = st.columns([1.55, 1])

    with left:
        st.markdown(
            '<div class="section-title">RESEARCH PROGRESS</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;">
                <strong>Engineering Progress</strong>
                <strong>{progress:.1f}%</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(progress / 100.0)

        st.markdown(
            f"""
            <div class="small-note">
                Active phase: {phase}<br>
                Current operation: {step}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-title">GIT STATUS</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        branch = git["branch"] or "unknown"
        commit = git["commit"] or "unknown"

        if git["status"]:
            git_state = "MODIFIED"
            git_class = "danger"
        else:
            git_state = "CLEAN"
            git_class = "success"

        st.markdown(
            f"""
            <div>
                <div class="small-note">BRANCH</div>
                <strong>{branch}</strong>
            </div>
            <br>
            <div>
                <div class="small-note">COMMIT</div>
                <code>{commit}</code>
            </div>
            <br>
            <div class="{git_class}">
                ● WORKTREE {git_state}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # LOWER LANDSCAPE AREA
    # ------------------------------------------------------------------

    left, center, right = st.columns([1.15, 1.35, 1])

    with left:
        st.markdown(
            '<div class="section-title">PHASE TIMELINE</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_timeline(state)
        st.markdown("</div>", unsafe_allow_html=True)

    with center:
        st.markdown(
            '<div class="section-title">EVENT STREAM</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_events(events)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-title">OWNER CONTROLS</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.write("Dashboard controls")

        auto_refresh = st.toggle(
            "Auto-refresh mode",
            value=False,
        )

        event_limit = st.slider(
            "Events displayed",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
        )

        events = load_events(limit=event_limit)

        if st.button(
            "Reload Event Stream",
            use_container_width=True,
        ):
            st.rerun()

        st.markdown("---")

        st.markdown(
            """
            <div class="small-note">
                Auto-refresh is intentionally opt-in.<br><br>
                Test execution remains controlled so the dashboard
                cannot accidentally launch arbitrary project commands.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if auto_refresh:
            st.info(
                "Auto-refresh selected. Use browser refresh or "
                "the dashboard refresh control."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # TEST COMMAND
    # ------------------------------------------------------------------

    if st.session_state.get("request_test_run"):
        st.session_state["request_test_run"] = False

        st.markdown(
            '<div class="section-title">TEST EXECUTION</div>',
            unsafe_allow_html=True,
        )

        with st.status("Running test suite...", expanded=True) as status_box:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            if result.stdout:
                st.code(result.stdout)

            if result.stderr:
                st.code(result.stderr)

            if result.returncode == 0:
                status_box.update(
                    label="Test suite passed",
                    state="complete",
                )
            else:
                status_box.update(
                    label="Test suite failed",
                    state="error",
                )

    # ------------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------------

    st.markdown(
        """
        <div style="
            margin-top:32px;
            padding-top:16px;
            border-top:1px solid rgba(190,205,230,0.12);
            color:#687890;
            text-align:center;
            font-size:0.8rem;
        ">
            EINSTEIN AI V2 · OWNER MONITORING SYSTEM · PHASE 0.6.4-U1
            <br>
            Research monitoring interface — not a biological reconstruction claim.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
