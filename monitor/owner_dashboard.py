"""
Einstein AI V2 — Owner Monitoring Dashboard

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

STATE_CANDIDATES = [
    PROJECT_ROOT / "project_state.json",
    MONITOR_DIR / "project_state.json",
    PROJECT_ROOT / "data" / "project_state.json",
]

EVENT_CANDIDATES = [
    PROJECT_ROOT / "audit_events.jsonl",
    PROJECT_ROOT / "monitoring_events.jsonl",
    MONITOR_DIR / "audit_events.jsonl",
    MONITOR_DIR / "monitoring_events.jsonl",
]


# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Einstein AI V2 — Owner Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# THEME
# ============================================================================

def inject_theme() -> None:
    """Apply the dashboard visual theme."""

    st.markdown(
        """
        <style>
        .main {
            padding-top: 1rem;
        }

        .dashboard-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            opacity: 0.75;
            margin-bottom: 1.5rem;
        }

        .dashboard-card {
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 1rem;
            background: rgba(128,128,128,0.06);
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
    """Load a JSON object."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if isinstance(data, dict):
            return data

        return {"data": data}

    except (OSError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSON Lines events."""

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


# ============================================================================
# PROJECT STATE
# ============================================================================

def load_project_state() -> dict[str, Any]:
    """Load project state with a safe fallback."""

    state_path = find_first_existing(STATE_CANDIDATES)

    if state_path is not None:
        state = load_json(state_path)

        if "error" not in state:
            return state

    return {
        "project": "Einstein AI V2",
        "version": "0.1.0",
        "status": "ACTIVE",
        "phase": "Monitoring System",
        "progress": 0,
        "state_source": "live fallback",
    }


# ============================================================================
# EVENTS
# ============================================================================

def load_events() -> list[dict[str, Any]]:
    """Load monitoring events."""

    event_path = find_first_existing(EVENT_CANDIDATES)

    if event_path is None:
        return []

    return load_jsonl(event_path)


def get_recent_events(
    events: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return recent events."""

    return events[-limit:][::-1]


# ============================================================================
# HELPERS
# ============================================================================

def get_value(
    data: dict[str, Any],
    keys: list[str],
    default: Any = None,
) -> Any:
    """Get the first matching dictionary value."""

    for key in keys:
        if key in data:
            return data[key]

    return default


def normalize_progress(value: Any) -> float:
    """Normalize progress to 0–100."""

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
    """Get Git branch, commit, and status."""

    branch_code, branch, branch_error = run_command(
        ["git", "branch", "--show-current"]
    )

    commit_code, commit, commit_error = run_command(
        ["git", "rev-parse", "--short", "HEAD"]
    )

    status_code, status, status_error = run_command(
        ["git", "status", "--short", "--branch"]
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


# ============================================================================
# VALIDATION
# ============================================================================

def run_pytest() -> tuple[bool, str]:
    """Run pytest."""

    code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "-q"],
        timeout=120,
    )

    return code == 0, stdout or stderr


def run_ruff() -> tuple[bool, str]:
    """Run Ruff."""

    code, stdout, stderr = run_command(
        [sys.executable, "-m", "ruff", "check", "."],
        timeout=120,
    )

    return code == 0, stdout or stderr


def run_foundation() -> tuple[bool, str]:
    """Run Einstein AI V2 foundation."""

    code, stdout, stderr = run_command(
        [sys.executable, "einstein_v2.py"],
        timeout=120,
    )

    return code == 0, stdout or stderr


# ============================================================================
# EVENT FORMATTING
# ============================================================================

def format_event(event: dict[str, Any]) -> str:
    """Format an event for display."""

    timestamp = get_value(
        event,
        ["timestamp", "time", "created_at", "datetime"],
        "",
    )

    event_type = get_value(
        event,
        ["event_type", "type", "event", "action"],
        "event",
    )

    message = get_value(
        event,
        ["message", "description", "details"],
        "",
    )

    return f"{timestamp} — {event_type} — {message}"


# ============================================================================
# HEADER
# ============================================================================

def render_header() -> None:
    """Render the main header."""

    st.markdown(
        '<div class="dashboard-title">🧠 Einstein AI V2</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        "Owner Monitoring & Engineering Control Dashboard"
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar() -> None:
    """Render owner controls."""

    st.sidebar.title("Owner Controls")

    st.sidebar.caption(
        "Einstein AI V2 monitoring system"
    )

    if st.sidebar.button(
        "🔄 Refresh Dashboard",
        use_container_width=True,
    ):
        st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("Project")

    st.sidebar.write(
        f"**Root:** `{PROJECT_ROOT}`"
    )

    st.sidebar.write(
        f"**Monitor:** `{MONITOR_DIR}`"
    )

    st.sidebar.divider()

    st.sidebar.subheader("Validation")

    if st.sidebar.button(
        "🧪 Run Tests",
        use_container_width=True,
    ):
        with st.spinner("Running pytest..."):
            passed, output = run_pytest()

        st.session_state["pytest_output"] = output

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

        if passed:
            st.sidebar.success("Ruff: PASS")
        else:
            st.sidebar.error("Ruff: FAIL")

    if st.sidebar.button(
        "▶ Run Einstein V2",
        use_container_width=True,
    ):
        with st.spinner("Running foundation..."):
            passed, output = run_foundation()

        st.session_state["foundation_output"] = output

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
    """Render project metrics."""

    progress = normalize_progress(
        get_value(
            state,
            ["progress", "progress_percent", "completion"],
            0,
        )
    )

    status = get_value(
        state,
        ["status", "project_status", "state"],
        "UNKNOWN",
    )

    phase = get_value(
        state,
        ["phase", "current_phase", "stage"],
        "Unknown",
    )

    version = get_value(
        state,
        ["version", "project_version"],
        "Unknown",
    )

    st.subheader("Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Status", str(status))

    with col2:
        st.metric("Version", str(version))

    with col3:
        st.metric("Current Phase", str(phase))

    with col4:
        st.metric("Progress", f"{progress:.1f}%")

    st.progress(progress / 100.0)


# ============================================================================
# GIT STATUS
# ============================================================================

def render_git_status() -> None:
    """Render Git repository information."""

    git = get_git_info()

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

    with st.expander("Git Status"):
        st.code(
            git["status"],
            language="text",
        )


# ============================================================================
# EVENTS
# ============================================================================

def render_events(
    events: list[dict[str, Any]],
) -> None:
    """Render monitoring events."""

    st.subheader("Monitoring Events")

    recent_events = get_recent_events(
        events,
        limit=10,
    )

    if not recent_events:
        st.info(
            "No monitoring events have been recorded yet."
        )
        return

    for event in recent_events:
        st.markdown(
            f'<div class="dashboard-card">'
            f"{format_event(event)}"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================================
# VALIDATION RESULTS
# ============================================================================

def render_validation_results() -> None:
    """Render validation output."""

    st.subheader("Validation Results")

    pytest_output = st.session_state.get(
        "pytest_output"
    )

    ruff_output = st.session_state.get(
        "ruff_output"
    )

    foundation_output = st.session_state.get(
        "foundation_output"
    )

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

    if not any(
        [
            pytest_output,
            ruff_output,
            foundation_output,
        ]
    ):
        st.info(
            "Use the validation controls in the sidebar "
            "to run project checks."
        )


# ============================================================================
# PROJECT FILES
# ============================================================================

def render_project_files() -> None:
    """Display important project files."""

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
            }
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
    """Render the complete owner dashboard."""

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


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    render_dashboard()
