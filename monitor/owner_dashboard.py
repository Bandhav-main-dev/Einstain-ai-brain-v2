"""
Einstein AI V2 — Owner Command Center.

Run from the repository root:

    streamlit run monitor/owner_dashboard.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MONITOR_DIR = PROJECT_ROOT / "monitor"

# Legacy/canonical paths retained for compatibility with the existing tests.
STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"

STATE_CANDIDATES = [
    STATE_FILE,
    PROJECT_ROOT / "project_state.json",
    MONITOR_DIR / "project_state.json",
    PROJECT_ROOT / "data" / "project_state.json",
]

EVENT_CANDIDATES = [
    EVENT_FILE,
    PROJECT_ROOT / "audit_events.jsonl",
    PROJECT_ROOT / "monitoring_events.jsonl",
    MONITOR_DIR / "audit_events.jsonl",
    MONITOR_DIR / "monitoring_events.jsonl",
]


# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Einstein AI V2 — Owner Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# THEME
# ============================================================================

def inject_theme() -> None:
    """Apply the Einstein AI V2 Bleach-inspired command-center theme."""

    st.markdown(
        """
        <style>

        /* ================================================================
           EINSTEIN AI V2 — OWNER COMMAND CENTER
           Original Bleach-inspired / spiritual-energy aesthetic
           ================================================================ */

        @import url(
            'https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap'
        );

        /* ----------------------------------------------------------------
           GLOBAL APPLICATION
           ---------------------------------------------------------------- */

        .stApp {
            background:
                radial-gradient(
                    circle at 15% 10%,
                    rgba(91, 33, 182, 0.22),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 85% 5%,
                    rgba(67, 56, 202, 0.20),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 50% 100%,
                    rgba(124, 58, 237, 0.14),
                    transparent 35%
                ),
                linear-gradient(
                    135deg,
                    #050507 0%,
                    #09090f 45%,
                    #050509 100%
                );

            color: #f5f3ff;
            font-family: 'Inter', sans-serif;
        }

        .main {
            padding-top: 0.5rem;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* ----------------------------------------------------------------
           SIDEBAR
           ---------------------------------------------------------------- */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    rgba(8, 8, 14, 0.98),
                    rgba(13, 10, 22, 0.98)
                );

            border-right: 1px solid rgba(139, 92, 246, 0.25);
            box-shadow:
                8px 0 35px rgba(0, 0, 0, 0.45);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-family: 'Cinzel', serif;
            letter-spacing: 0.05em;
        }

        /* ----------------------------------------------------------------
           OWNER HEADER
           ---------------------------------------------------------------- */

        .owner-hero {
            position: relative;
            overflow: hidden;

            padding: 2rem 2.2rem;
            margin-bottom: 1.5rem;

            border-radius: 20px;

            background:
                linear-gradient(
                    135deg,
                    rgba(17, 17, 27, 0.97),
                    rgba(24, 17, 40, 0.92)
                );

            border: 1px solid rgba(139, 92, 246, 0.40);

            box-shadow:
                0 0 0 1px rgba(255,255,255,0.02),
                0 20px 55px rgba(0,0,0,0.45),
                0 0 45px rgba(124,58,237,0.10);
        }

        .owner-hero::before {
            content: "";
            position: absolute;
            left: -20%;
            top: 0;
            width: 70%;
            height: 2px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(196,181,253,0.95),
                    transparent
                );

            box-shadow:
                0 0 15px rgba(167,139,250,0.90),
                0 0 35px rgba(124,58,237,0.60);

            animation: reiatsu-flow 5s linear infinite;
        }

        @keyframes reiatsu-flow {
            0% {
                transform: translateX(-20%);
                opacity: 0.25;
            }

            50% {
                opacity: 1;
            }

            100% {
                transform: translateX(190%);
                opacity: 0.25;
            }
        }

        .owner-eyebrow {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: #a78bfa;
            margin-bottom: 0.65rem;
        }

        .owner-title {
            font-family: 'Cinzel', serif;
            font-size: clamp(2rem, 4vw, 3.5rem);
            font-weight: 800;
            letter-spacing: 0.08em;
            line-height: 1.05;
            color: #faf5ff;

            text-shadow:
                0 0 10px rgba(196,181,253,0.35),
                0 0 30px rgba(124,58,237,0.20);

            margin: 0;
        }

        .owner-subtitle {
            margin-top: 0.8rem;
            color: #aaa3b8;
            font-size: 0.92rem;
            letter-spacing: 0.06em;
        }

        .reiatsu-line {
            height: 1px;
            margin-top: 1.2rem;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(167,139,250,0.85),
                    rgba(255,255,255,0.55),
                    rgba(167,139,250,0.85),
                    transparent
                );

            box-shadow:
                0 0 12px rgba(139,92,246,0.50);
        }

        /* ----------------------------------------------------------------
           SECTION TITLES
           ---------------------------------------------------------------- */

        .section-title {
            font-family: 'Cinzel', serif;
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #ede9fe;

            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }

        .section-title::before {
            content: "◈";
            color: #a78bfa;
            margin-right: 0.6rem;

            text-shadow:
                0 0 10px rgba(167,139,250,0.80);
        }

        /* ----------------------------------------------------------------
           TELEMETRY CARDS
           ---------------------------------------------------------------- */

        .telemetry-card {
            position: relative;
            min-height: 120px;

            padding: 1.15rem;

            border-radius: 15px;

            background:
                linear-gradient(
                    145deg,
                    rgba(18,18,27,0.95),
                    rgba(26,20,39,0.86)
                );

            border: 1px solid rgba(139,92,246,0.23);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.035),
                0 10px 30px rgba(0,0,0,0.25);

            transition:
                transform 0.25s ease,
                border-color 0.25s ease,
                box-shadow 0.25s ease;
        }

        .telemetry-card:hover {
            transform: translateY(-3px);

            border-color:
                rgba(167,139,250,0.55);

            box-shadow:
                0 12px 35px rgba(0,0,0,0.35),
                0 0 25px rgba(124,58,237,0.12);
        }

        .telemetry-label {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: #8f879e;
        }

        .telemetry-value {
            margin-top: 0.45rem;

            font-family: 'Cinzel', serif;
            font-size: 1.45rem;
            font-weight: 700;

            color: #f5f3ff;

            text-shadow:
                0 0 12px rgba(167,139,250,0.20);
        }

        /* ----------------------------------------------------------------
           STREAMLIT METRICS
           ---------------------------------------------------------------- */

        [data-testid="stMetric"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(18,18,27,0.95),
                    rgba(26,20,39,0.86)
                );

            border: 1px solid rgba(139,92,246,0.23);
            border-radius: 15px;

            padding: 1rem;

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.03),
                0 10px 30px rgba(0,0,0,0.25);
        }

        [data-testid="stMetricLabel"] {
            color: #8f879e !important;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            color: #f5f3ff !important;
            font-family: 'Cinzel', serif;
        }

        /* ----------------------------------------------------------------
           PROGRESS BAR — REIATSU
           ---------------------------------------------------------------- */

        [data-testid="stProgress"] {
            margin-top: 0.8rem;
            margin-bottom: 1rem;
        }

        [data-testid="stProgressBar"] {
            background: rgba(255,255,255,0.06);
            border-radius: 99px;
        }

        [data-testid="stProgressBar"] > div {
            background:
                linear-gradient(
                    90deg,
                    #6d28d9,
                    #8b5cf6,
                    #c4b5fd
                );

            box-shadow:
                0 0 12px rgba(139,92,246,0.75),
                0 0 28px rgba(124,58,237,0.30);
        }

        /* ----------------------------------------------------------------
           EVENT CARDS
           ---------------------------------------------------------------- */

        .event-card {
            position: relative;

            padding: 0.95rem 1.1rem;
            margin-bottom: 0.7rem;

            border-radius: 12px;

            background:
                linear-gradient(
                    90deg,
                    rgba(20,17,30,0.95),
                    rgba(13,13,20,0.90)
                );

            border: 1px solid rgba(139,92,246,0.18);
            border-left: 3px solid #8b5cf6;

            box-shadow:
                0 8px 22px rgba(0,0,0,0.22);
        }

        .event-time {
            color: #80788c;
            font-size: 0.72rem;
            letter-spacing: 0.04em;
        }

        .event-message {
            margin-top: 0.25rem;
            color: #eeeaf7;
            font-weight: 600;
        }

        /* ----------------------------------------------------------------
           STATUS INDICATOR
           ---------------------------------------------------------------- */

        .system-online {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;

            padding: 0.35rem 0.7rem;

            border-radius: 999px;

            background: rgba(16,185,129,0.08);
            border: 1px solid rgba(16,185,129,0.28);

            color: #a7f3d0;

            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .system-online::before {
            content: "";
            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #34d399;

            box-shadow:
                0 0 8px rgba(52,211,153,0.90),
                0 0 16px rgba(52,211,153,0.50);

            animation: pulse-online 1.8s ease-in-out infinite;
        }

        @keyframes pulse-online {
            0%, 100% {
                opacity: 0.55;
                transform: scale(0.85);
            }

            50% {
                opacity: 1;
                transform: scale(1.15);
            }
        }

        /* ----------------------------------------------------------------
           BUTTONS
           ---------------------------------------------------------------- */

        .stButton > button {
            border-radius: 10px;

            border: 1px solid rgba(139,92,246,0.30);

            background:
                linear-gradient(
                    135deg,
                    rgba(91,33,182,0.28),
                    rgba(30,27,48,0.90)
                );

            color: #f5f3ff;

            font-weight: 600;

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);

            border-color:
                rgba(196,181,253,0.65);

            box-shadow:
                0 0 20px rgba(124,58,237,0.22);
        }

        /* ----------------------------------------------------------------
           EXPANDERS
           ---------------------------------------------------------------- */

        [data-testid="stExpander"] {
            border: 1px solid rgba(139,92,246,0.20);
            border-radius: 12px;
            background: rgba(12,12,18,0.65);
        }

        /* ----------------------------------------------------------------
           DATAFRAMES
           ---------------------------------------------------------------- */

        [data-testid="stDataFrame"] {
            border: 1px solid rgba(139,92,246,0.20);
            border-radius: 12px;
            overflow: hidden;
        }

        /* ----------------------------------------------------------------
           DIVIDERS
           ---------------------------------------------------------------- */

        hr {
            border: 0;
            height: 1px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(139,92,246,0.30),
                    rgba(255,255,255,0.12),
                    rgba(139,92,246,0.30),
                    transparent
                );

            margin: 1.4rem 0;
        }

        /* ----------------------------------------------------------------
           CAPTIONS / FOOTER
           ---------------------------------------------------------------- */

        .small-text,
        [data-testid="stCaptionContainer"] {
            color: #777080;
        }

        /* ----------------------------------------------------------------
           SCROLLBAR
           ---------------------------------------------------------------- */

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #07070b;
        }

        ::-webkit-scrollbar-thumb {
            background: #31234d;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #6d28d9;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# FILE DISCOVERY
# ============================================================================

def find_first_existing(paths: list[Path]) -> Path | None:
    """Return the first existing path."""

    for path in paths:
        if path.exists():
            return path

    return None


# ============================================================================
# DATA LOADING
# ============================================================================

def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object safely."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if isinstance(data, dict):
            return data

        return {}

    except (OSError, json.JSONDecodeError):
        return {}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSON Lines events safely."""

    events: list[dict[str, Any]] = []

    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                try:
                    value = json.loads(line)

                    if isinstance(value, dict):
                        events.append(value)

                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    return events


def load_project_state() -> dict[str, Any]:
    """
    Load the project state.

    STATE_FILE is checked first so existing monitoring tests and
    monitoring components can override it safely.
    """

    if STATE_FILE.exists():
        return load_json(STATE_FILE)

    state_path = find_first_existing(
        [
            path
            for path in STATE_CANDIDATES
            if path != STATE_FILE
        ]
    )

    if state_path is None:
        return {}

    return load_json(state_path)


def load_state() -> dict[str, Any]:
    """Backward-compatible alias for load_project_state()."""

    if not STATE_FILE.exists():
        return {}

    return load_json(STATE_FILE)


def load_events() -> list[dict[str, Any]]:
    """Load monitoring events, newest first.

    EVENT_FILE is checked first so monkeypatch-based tests remain
    compatible with the dashboard's original interface.
    """

    event_path = EVENT_FILE

    if not event_path.exists():
        event_path = find_first_existing(EVENT_CANDIDATES)

    if event_path is None or not event_path.exists():
        return []

    return load_jsonl(event_path)[::-1]


def get_recent_events(
    events: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return newest events first."""

    return list(reversed(events[-limit:]))


# ============================================================================
# HELPERS
# ============================================================================

def get_value(
    data: dict[str, Any],
    keys: list[str],
    default: Any = None,
) -> Any:
    """Return the first matching dictionary value."""

    for key in keys:
        if key in data:
            return data[key]

    return default


def normalize_progress(value: Any) -> float:
    """Normalize progress to the 0–100 range."""

    try:
        progress = float(value)
    except (TypeError, ValueError):
        return 0.0

    if 0 <= progress <= 1:
        progress *= 100

    return max(0.0, min(100.0, progress))


# ============================================================================
# GIT
# ============================================================================

def run_command(
    command: list[str],
    timeout: int = 30,
) -> tuple[int, str, str]:
    """Run a command from the project root."""

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except (OSError, subprocess.SubprocessError) as exc:
        return 1, "", str(exc)


def get_git_info() -> dict[str, str]:
    """Return Git branch, commit, and status."""

    branch_code, branch, branch_error = run_command(
        ["git", "branch", "--show-current"],
    )

    commit_code, commit, commit_error = run_command(
        ["git", "rev-parse", "--short", "HEAD"],
    )

    status_code, status, status_error = run_command(
        ["git", "status", "--short", "--branch"],
    )

    return {
        "branch": (
            branch
            if branch_code == 0
            else f"Unavailable: {branch_error}"
        ),
        "commit": (
            commit
            if commit_code == 0
            else f"Unavailable: {commit_error}"
        ),
        "status": (
            status
            if status_code == 0
            else f"Unavailable: {status_error}"
        ),
    }


def git_info() -> dict[str, str]:
    """
    Backward-compatible Git information API.

    Existing tests and older monitoring components expect this name.
    """

    return get_git_info()


# ============================================================================
# VALIDATION
# ============================================================================

def run_pytest() -> tuple[bool, str]:
    """Run the full pytest suite."""

    code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "-q"],
        timeout=120,
    )

    return code == 0, stdout or stderr


def run_ruff() -> tuple[bool, str]:
    """Run Ruff against the repository."""

    code, stdout, stderr = run_command(
        [sys.executable, "-m", "ruff", "check", "."],
        timeout=120,
    )

    return code == 0, stdout or stderr


def run_foundation() -> tuple[bool, str]:
    """Run the Einstein AI V2 foundation."""

    code, stdout, stderr = run_command(
        [sys.executable, "einstein_v2.py"],
        timeout=120,
    )

    return code == 0, stdout or stderr


# ============================================================================
# HEADER
# ============================================================================

def render_header() -> None:
    """Render the owner command center header."""

    st.markdown(
        '<div class="dashboard-title">'
        "🧠 EINSTEIN AI V2 — OWNER COMMAND CENTER"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        "Private engineering control center • "
        "Project state • Progress • Git • Tests • Monitoring"
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar() -> None:
    """Render owner controls."""

    st.sidebar.title("Owner Controls")
    st.sidebar.caption("Einstein AI V2 monitoring system")

    if st.sidebar.button(
        "🔄 Refresh Dashboard",
        use_container_width=True,
    ):
        st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("Validation")

    if st.sidebar.button(
        "🧪 Run Tests",
        use_container_width=True,
    ):
        with st.spinner("Running pytest..."):
            passed, output = run_pytest()

        st.session_state["pytest_output"] = output
        st.session_state["pytest_passed"] = passed

        if passed:
            st.sidebar.success("Pytest: PASS")
        else:
            st.sidebar.error("Pytest: FAIL")

    if st.sidebar.button(
        "🔎 Run Ruff",
        use_container_width=True,
    ):
        with st.spinner("Running Ruff..."):
            passed, output = run_ruff()

        st.session_state["ruff_output"] = output
        st.session_state["ruff_passed"] = passed

        if passed:
            st.sidebar.success("Ruff: PASS")
        else:
            st.sidebar.error("Ruff: FAIL")

    if st.sidebar.button(
        "▶ Run Einstein V2",
        use_container_width=True,
    ):
        with st.spinner("Running Einstein AI V2..."):
            passed, output = run_foundation()

        st.session_state["foundation_output"] = output
        st.session_state["foundation_passed"] = passed

        if passed:
            st.sidebar.success("Foundation: PASS")
        else:
            st.sidebar.error("Foundation: FAIL")


# ============================================================================
# PROJECT OVERVIEW
# ============================================================================

def render_project_overview(
    state: dict[str, Any],
) -> None:
    """Render high-level project metrics."""

    progress = normalize_progress(
        get_value(
            state,
            [
                "progress",
                "progress_percent",
                "overall_progress",
                "completion",
            ],
            0,
        ),
    )

    status = get_value(
        state,
        ["status", "project_status", "state"],
        "UNKNOWN",
    )

    phase = get_value(
        state,
        ["phase", "current_phase", "stage"],
        "Monitoring System",
    )

    step = get_value(
        state,
        ["step", "current_step"],
        "Unknown",
    )

    version = get_value(
        state,
        ["version", "project_version"],
        "0.1.0",
    )

    st.subheader("Project Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Status", str(status))

    with col2:
        st.metric("Version", str(version))

    with col3:
        st.metric("Phase", str(phase))

    with col4:
        st.metric("Step", str(step))

    with col5:
        st.metric("Progress", f"{progress:.1f}%")

    st.progress(progress / 100.0)


# ============================================================================
# GIT STATUS
# ============================================================================

def render_git_status() -> None:
    """Render Git repository information."""

    git = git_info()

    st.subheader("SYSTEM TELEMETRY")

    st.caption("Live repository and engineering telemetry")

    st.subheader("Git Repository")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Branch",
            git["branch"] or "Unknown",
        )

    with col2:
        st.metric(
            "Commit",
            git["commit"] or "Unknown",
        )

    with st.expander("Git Status", expanded=False):
        st.code(
            git["status"],
            language="text",
        )


# ============================================================================
# EVENTS
# ============================================================================

def format_event(event: dict[str, Any]) -> str:
    """Format a monitoring event."""

    timestamp = get_value(
        event,
        ["timestamp", "time", "created_at", "datetime"],
        "Unknown time",
    )

    event_type = get_value(
        event,
        ["event_type", "type", "event", "action"],
        "EVENT",
    )

    message = get_value(
        event,
        ["message", "description", "details"],
        "",
    )

    return f"{timestamp} — {event_type} — {message}"


def render_events(
    events: list[dict[str, Any]],
) -> None:
    """Render recent monitoring events."""

    st.subheader("Monitoring Events")

    recent_events = get_recent_events(
        events,
        limit=10,
    )

    if not recent_events:
        st.info(
            "No monitoring events have been recorded yet.",
        )
        return

    for event in recent_events:
        st.markdown(
            '<div class="dashboard-card">'
            f"{format_event(event)}"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================================
# VALIDATION RESULTS
# ============================================================================

def render_validation_results() -> None:
    """Render validation outputs."""

    st.subheader("Engineering Validation")

    pytest_output = st.session_state.get("pytest_output")
    ruff_output = st.session_state.get("ruff_output")
    foundation_output = st.session_state.get("foundation_output")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.get("pytest_passed") is True:
            st.success("Pytest PASS")
        elif st.session_state.get("pytest_passed") is False:
            st.error("Pytest FAIL")
        else:
            st.info("Pytest not run")

    with col2:
        if st.session_state.get("ruff_passed") is True:
            st.success("Ruff PASS")
        elif st.session_state.get("ruff_passed") is False:
            st.error("Ruff FAIL")
        else:
            st.info("Ruff not run")

    with col3:
        if st.session_state.get("foundation_passed") is True:
            st.success("Foundation PASS")
        elif st.session_state.get("foundation_passed") is False:
            st.error("Foundation FAIL")
        else:
            st.info("Foundation not run")

    if pytest_output:
        with st.expander("Pytest Output"):
            st.code(
                pytest_output,
                language="text",
            )

    if ruff_output:
        with st.expander("Ruff Output"):
            st.code(
                ruff_output,
                language="text",
            )

    if foundation_output:
        with st.expander("Einstein V2 Output"):
            st.code(
                foundation_output,
                language="text",
            )


# ============================================================================
# PROJECT FILES
# ============================================================================

def render_project_files() -> None:
    """Display important Einstein AI V2 files."""

    st.subheader("Project Structure")

    important_files = [
        "einstein_v2.py",
        "requirements.txt",
        "README.md",
        "monitor/__init__.py",
        "monitor/owner_dashboard.py",
        "monitor/professor_dashboard.py",
        "monitor/auth.py",
        "monitor/project_state.py",
        "monitor/progress.py",
        "monitor/logging_core.py",
        "tests/test_owner_dashboard.py",
        "tests/test_professor_dashboard.py",
    ]

    rows: list[dict[str, str]] = []

    for relative_path in important_files:
        path = PROJECT_ROOT / relative_path

        rows.append(
            {
                "File": relative_path,
                "Status": (
                    "PRESENT"
                    if path.exists()
                    else "MISSING"
                ),
            },
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================================
# FOOTER
# ============================================================================

def render_footer() -> None:
    """Render dashboard footer."""

    st.divider()

    now = datetime.now().astimezone()

    st.caption(
        "Einstein AI V2 Owner Monitoring System • "
        f"Dashboard time: {now:%Y-%m-%d %H:%M:%S %Z}"
    )


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def render_dashboard() -> None:
    """Render the complete owner command center."""

    inject_theme()
    render_sidebar()
    render_header()

    state = load_project_state()
    events = load_events()

    render_project_overview(state)

    st.divider()

    render_git_status()

    st.divider()

    render_events(events)

    st.divider()

    render_validation_results()

    st.divider()

    render_project_files()

    render_footer()


if __name__ == "__main__":
    render_dashboard()
