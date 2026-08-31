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

EVENTS_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"


def load_project_state() -> dict[str, Any]:
    """Load project monitoring state."""
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_events() -> list[dict[str, Any]]:
    """Load monitoring events."""
    if not EVENTS_FILE.exists():
        return []

    events = []

    for line in EVENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return events


def run_tests() -> tuple[int, str]:
    """Run the Einstein AI V2 test suite."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    output = result.stdout + result.stderr

    return result.returncode, output


def render_dashboard() -> None:
    """Render the professor/test dashboard."""
    st.set_page_config(
        page_title=("Einstein AI V2 — Professor Dashboard"),
        page_icon="🧠",
        layout="wide",
    )

    if not login_form():
        return

    if not require_role("professor"):
        st.error("Professor access required.")

        if st.button("Logout"):
            logout()

        return

    state = load_project_state()
    events = load_events()

    st.title("🧠 Einstein AI V2")

    st.subheader("Professor / Test Dashboard")

    username = st.session_state.get(
        "username",
        "unknown",
    )

    st.caption(f"Authenticated as: {username} | Role: professor")

    if st.button("Logout"):
        logout()

    st.divider()

    progress = float(
        state.get(
            "overall_progress",
            state.get(
                "progress_percent",
                0.0,
            ),
        )
    )

    phase = state.get(
        "current_phase",
        "unknown",
    )

    step = state.get(
        "current_step",
        "unknown",
    )

    status = state.get(
        "status",
        "unknown",
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Overall Progress",
        f"{progress:.1f}%",
    )

    col2.metric(
        "Current Phase",
        str(phase),
    )

    col3.metric(
        "Status",
        str(status),
    )

    col4.metric(
        "Events",
        len(events),
    )

    st.progress(
        max(
            0.0,
            min(
                progress / 100.0,
                1.0,
            ),
        )
    )

    st.info(f"Current step: {step}")

    st.divider()

    st.subheader("Project State")

    if state:
        st.json(state)
    else:
        st.warning("Project state is unavailable.")

    st.divider()

    st.subheader("Test Execution")

    if st.button(
        "Run Full Test Suite",
        type="primary",
    ):
        with st.spinner("Running pytest..."):
            return_code, output = run_tests()

        if return_code == 0:
            st.success("All tests completed successfully.")
        else:
            st.error(f"Test suite failed with exit code {return_code}.")

        st.code(
            output,
            language="text",
        )

    st.divider()

    st.subheader("Monitoring Events")

    if events:
        st.dataframe(
            events[-50:],
            use_container_width=True,
        )
    else:
        st.info("No monitoring events recorded yet.")


if __name__ == "__main__":
    render_dashboard()
