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
    """Apply the owner dashboard visual theme."""

    st.markdown(
        """
        <style>
        .main {
            padding-top: 1rem;
        }

        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin-bottom: 0.2rem;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            opacity: 0.75;
            margin-bottom: 1.5rem;
        }

        .dashboard-card {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            background: rgba(128, 128, 128, 0.06);
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
        }

        .small-text {
            font-size: 0.8rem;
            opacity: 0.7;
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
