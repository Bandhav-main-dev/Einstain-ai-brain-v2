
"""
Einstein AI V2 — Owner Zanpakutō Command Center.

Purpose
-------
This dashboard is an OWNER CONTROL CENTER.

It is designed to answer:

    What has been completed?
    What is currently being worked on?
    What remains?
    What should happen next?
    What does the owner need to do?

Developer validation commands are intentionally NOT presented as
owner controls.

Run:

    streamlit run monitor/owner_dashboard.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st

# =============================================================================
# PROJECT PATHS
# =============================================================================

OWNER_FILE = Path(__file__).resolve()
PROJECT_ROOT = OWNER_FILE.parent.parent

STATE_FILE = PROJECT_ROOT / "logs" / "project_state.json"
EVENT_FILE = PROJECT_ROOT / "logs" / "project_events.jsonl"


# =============================================================================
# PAGE
# =============================================================================

st.set_page_config(
    page_title="Einstein AI V2 — Zanpakutō Command Center",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# THEME
# =============================================================================

def inject_theme() -> None:
    st.markdown(
        """
        <style>

        :root {
            --red: #c1121f;
            --dark-red: #780000;
            --black: #050505;
            --black2: #101010;
            --white: #f8f8f8;
            --gold: #d4af37;
            --gold2: #f2d675;
            --gray: #b8b8b8;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 50% 5%,
                    rgba(193,18,31,0.20),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 90% 70%,
                    rgba(212,175,55,0.08),
                    transparent 28%
                ),
                linear-gradient(
                    135deg,
                    #030303 0%,
                    #0b0b0b 45%,
                    #120000 100%
                );
            color: var(--white);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #050505,
                    #100000,
                    #050505
                );
            border-right: 1px solid rgba(212,175,55,0.35);
        }

        [data-testid="stSidebar"] * {
            color: var(--white);
        }

        .main-title {
            font-size: 3.1rem;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-align: center;
            color: var(--white);
            text-shadow:
                0 0 8px rgba(193,18,31,0.9),
                0 0 22px rgba(193,18,31,0.45);
            margin-bottom: 0.1rem;
        }

        .subtitle {
            text-align: center;
            color: var(--gold2);
            letter-spacing: 0.28em;
            font-size: 0.85rem;
            margin-bottom: 2rem;
        }

        .blade-line {
            height: 3px;
            background:
                linear-gradient(
                    90deg,
                    transparent,
                    var(--red),
                    var(--gold),
                    var(--red),
                    transparent
                );
            box-shadow: 0 0 15px rgba(193,18,31,0.8);
            margin: 15px 0 30px 0;
        }

        .section-title {
            color: var(--gold2);
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            border-left: 4px solid var(--red);
            padding-left: 12px;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .card {
            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.055),
                    rgba(255,255,255,0.015)
                );
            border: 1px solid rgba(212,175,55,0.28);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow:
                0 0 20px rgba(0,0,0,0.35),
                inset 0 0 20px rgba(193,18,31,0.025);
        }

        .card:hover {
            border-color: rgba(212,175,55,0.65);
            transform: translateY(-2px);
            transition: 0.25s ease;
        }

        .mission-card {
            background:
                linear-gradient(
                    135deg,
                    rgba(120,0,0,0.45),
                    rgba(15,15,15,0.96)
                );
            border: 1px solid var(--red);
            border-left: 6px solid var(--gold);
            border-radius: 16px;
            padding: 25px;
            box-shadow:
                0 0 25px rgba(193,18,31,0.20);
        }

        .mission-title {
            color: var(--gold2);
            font-size: 1.55rem;
            font-weight: 900;
            letter-spacing: 0.08em;
        }

        .mission-text {
            color: var(--white);
            font-size: 1.05rem;
            line-height: 1.65;
        }

        .status-complete {
            color: #ffffff;
            background: #650000;
            border: 1px solid var(--red);
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 700;
        }

        .status-active {
            color: #080808;
            background: var(--gold2);
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 900;
        }

        .status-locked {
            color: var(--gray);
            background: #181818;
            border: 1px solid #444;
            padding: 5px 10px;
            border-radius: 20px;
        }

        .step-number {
            color: var(--gold2);
            font-size: 1.7rem;
            font-weight: 900;
        }

        .step-title {
            color: var(--white);
            font-size: 1.15rem;
            font-weight: 800;
        }

        .step-description {
            color: #cfcfcf;
            line-height: 1.55;
        }

        .owner-action {
            background: rgba(193,18,31,0.13);
            border-left: 4px solid var(--red);
            padding: 12px 15px;
            border-radius: 7px;
            margin-top: 10px;
        }

        .system-action {
            background: rgba(212,175,55,0.08);
            border-left: 4px solid var(--gold);
            padding: 12px 15px;
            border-radius: 7px;
            margin-top: 10px;
        }

        .event-card {
            background: rgba(255,255,255,0.035);
            border-bottom: 1px solid rgba(212,175,55,0.16);
            padding: 12px;
        }

        .reiatsu-flow {
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0% {
                box-shadow: 0 0 5px rgba(193,18,31,0.1);
            }
            50% {
                box-shadow: 0 0 28px rgba(193,18,31,0.28);
            }
            100% {
                box-shadow: 0 0 5px rgba(193,18,31,0.1);
            }
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(212,175,55,0.22);
            border-radius: 12px;
            padding: 14px;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--gold2);
        }

        div[data-testid="stMetricValue"] {
            color: var(--white);
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme()


# =============================================================================
# DATA
# =============================================================================

def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def load_events() -> list[dict[str, Any]]:
    if not EVENT_FILE.exists():
        return []

    events: list[dict[str, Any]] = []

    try:
        lines = EVENT_FILE.read_text(encoding="utf-8").splitlines()

        for line in lines:
            if not line.strip():
                continue

            try:
                item = json.loads(line)

                if isinstance(item, dict):
                    events.append(item)

            except json.JSONDecodeError:
                continue

    except OSError:
        return []

    return list(reversed(events))


def git_info() -> dict[str, str]:
    def run(command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            return result.stdout.strip()

        except OSError:
            return ""

    return {
        "branch": run(["git", "branch", "--show-current"]),
        "commit": run(["git", "log", "-1", "--oneline"]),
        "status": run(["git", "status", "--short"]),
    }


# =============================================================================
# PROJECT ROADMAP
# =============================================================================

ROADMAP = [
    {
        "id": "0",
        "title": "Project Foundation",
        "status": "COMPLETE",
        "description": (
            "Establish the Einstein AI V2 repository, project structure, "
            "branch strategy, basic entry point, documentation and CI foundation."
        ),
        "owner": "Review project direction and approve the foundation.",
        "system": "Maintain the project structure and engineering foundation.",
    },
    {
        "id": "0.6",
        "title": "Monitoring System",
        "status": "COMPLETE",
        "description": (
            "Build the monitoring infrastructure that records project state, "
            "events, progress and development activity."
        ),
        "owner": "Use the dashboard to understand project status.",
        "system": "Record project events and maintain monitoring information.",
    },
    {
        "id": "0.6.4",
        "title": "Owner Command Center",
        "status": "COMPLETE",
        "description": (
            "Create the owner-facing control center for project visibility, "
            "roadmap tracking and mission management."
        ),
        "owner": "Review the roadmap and decide the next project priority.",
        "system": "Display progress, missions, milestones and project state.",
    },
    {
        "id": "0.7",
        "title": "Data & Knowledge Pipeline",
        "status": "NEXT",
        "description": (
            "Build the controlled knowledge acquisition, cleaning, validation "
            "and dataset preparation pipeline required for Einstein AI V2."
        ),
        "owner": (
            "Approve the target knowledge domains and decide which sources "
            "should be included."
        ),
        "system": (
            "Acquire, normalize, validate and prepare approved knowledge "
            "for downstream reasoning systems."
        ),
    },
    {
        "id": "0.8",
        "title": "Reasoning Architecture",
        "status": "PLANNED",
        "description": (
            "Construct the cognitive and reasoning architecture that combines "
            "retrieval, hypothesis generation, analogy, abstraction, critique "
            "and multi-step problem solving."
        ),
        "owner": "Define priorities for the reasoning capabilities.",
        "system": "Implement and evaluate the reasoning components.",
    },
    {
        "id": "0.9",
        "title": "Expert / MoE Architecture",
        "status": "PLANNED",
        "description": (
            "Develop specialized reasoning experts and an orchestration layer "
            "that can select or combine experts for different problem types."
        ),
        "owner": "Choose important expert domains.",
        "system": "Train, evaluate and orchestrate specialist modules.",
    },
    {
        "id": "1.0",
        "title": "Einstein-Style Research Engine",
        "status": "PLANNED",
        "description": (
            "Develop the research workflow for generating hypotheses, "
            "connecting concepts, exploring unconventional approaches and "
            "producing structured research documents."
        ),
        "owner": "Review research goals and evaluate generated ideas.",
        "system": "Generate, test, critique and refine candidate hypotheses.",
    },
    {
        "id": "1.1",
        "title": "Evaluation & Benchmarking",
        "status": "PLANNED",
        "description": (
            "Create benchmarks for reasoning quality, creativity, scientific "
            "problem solving, consistency, factual grounding and research output."
        ),
        "owner": "Define what successful Einstein-like reasoning means for the project.",
        "system": "Run controlled evaluations and track performance.",
    },
    {
        "id": "1.2",
        "title": "Full AI Integration",
        "status": "PLANNED",
        "description": (
            "Integrate the knowledge system, reasoning experts, memory, "
            "research engine and owner monitoring system into one platform."
        ),
        "owner": "Approve integration milestones and final product direction.",
        "system": "Integrate and validate all major subsystems.",
    },
]


# =============================================================================
# CURRENT PROJECT STATE
# =============================================================================

state = load_state()
events = load_events()
git = git_info()

completed_count = sum(
    1 for item in ROADMAP if item["status"] == "COMPLETE"
)

total_count = len(ROADMAP)

progress = round((completed_count / total_count) * 100, 1)

active = next(
    (
        item
        for item in ROADMAP
        if item["status"] == "NEXT"
    ),
    ROADMAP[0],
)


# =============================================================================
# HEADER
# =============================================================================

st.markdown(
    '<div class="main-title reiatsu-flow">⚔️ ZANPAKUTŌ COMMAND CENTER</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">EINSTEIN AI V2 • OWNER CONTROL SYSTEM</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="blade-line"></div>', unsafe_allow_html=True)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown("## ⚔️ OWNER CONTROL")

    st.markdown(
        """
        <div class="card">
        <b>Purpose</b><br><br>
        This dashboard is your command center for Einstein AI V2.
        <br><br>
        It shows what has been completed, what is active,
        what remains and what you need to decide.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")

    page = st.radio(
        "Select",
        [
            "Command Center",
            "Project Roadmap",
            "Current Mission",
            "Completed Work",
            "Remaining Work",
            "Project Events",
            "Project Information",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.caption("OWNER MODE")
    st.caption("Developer controls hidden")
    st.caption("Read-only engineering status")


# =============================================================================
# COMMAND CENTER
# =============================================================================

if page == "Command Center":

    st.markdown(
        '<div class="section-title">⚔️ PROJECT STATUS</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Overall Progress",
            f"{progress}%",
        )

    with col2:
        st.metric(
            "Completed",
            f"{completed_count}/{total_count}",
        )

    with col3:
        st.metric(
            "Next Mission",
            active["id"],
        )

    with col4:
        st.metric(
            "Events",
            len(events),
        )

    st.progress(progress / 100)

    st.markdown(
        '<div class="section-title">🔥 NEXT MISSION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="mission-card reiatsu-flow">

        <div class="mission-title">
        ⚔️ {active["id"]} — {active["title"]}
        </div>

        <br>

        <div class="mission-text">
        {active["description"]}
        </div>

        <br>

        <div class="owner-action">
        <b>👑 YOUR ROLE</b><br>
        {active["owner"]}
        </div>

        <div class="system-action">
        <b>🤖 SYSTEM ROLE</b><br>
        {active["system"]}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">📡 SYSTEM TELEMETRY</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.write(
        "Project monitoring information is available through the "
        "command center, roadmap, mission and project history views."
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">🗺️ PROJECT ROADMAP</div>',
        unsafe_allow_html=True,
    )

    for item in ROADMAP:

        if item["status"] == "COMPLETE":
            badge = '<span class="status-complete">✓ COMPLETE</span>'

        elif item["status"] == "NEXT":
            badge = '<span class="status-active">⚡ NEXT</span>'

        else:
            badge = '<span class="status-locked">○ PLANNED</span>'

        st.markdown(
            f"""
            <div class="card">

            <span class="step-number">
            {item["id"]}
            </span>

            &nbsp;&nbsp;

            <span class="step-title">
            {item["title"]}
            </span>

            &nbsp;&nbsp;

            {badge}

            <br><br>

            <div class="step-description">
            {item["description"]}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# ROADMAP
# =============================================================================

elif page == "Project Roadmap":

    st.markdown(
        '<div class="section-title">🗺️ COMPLETE PROJECT ROADMAP</div>',
        unsafe_allow_html=True,
    )

    for item in ROADMAP:

        st.markdown(
            f"""
            <div class="card">

            <div class="step-number">
            STEP {item["id"]}
            </div>

            <div class="step-title">
            {item["title"]}
            </div>

            <br>

            {item["description"]}

            <br><br>

            <div class="owner-action">
            <b>OWNER</b><br>
            {item["owner"]}
            </div>

            <div class="system-action">
            <b>SYSTEM</b><br>
            {item["system"]}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# CURRENT MISSION
# =============================================================================

elif page == "Current Mission":

    st.markdown(
        '<div class="section-title">⚔️ CURRENT MISSION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="mission-card reiatsu-flow">

        <div class="mission-title">
        {active["id"]} — {active["title"]}
        </div>

        <br>

        <div class="mission-text">
        {active["description"]}
        </div>

        <br>

        <div class="owner-action">
        <b>WHAT YOU NEED TO DO</b><br>
        {active["owner"]}
        </div>

        <div class="system-action">
        <b>WHAT THE SYSTEM NEEDS TO DO</b><br>
        {active["system"]}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "This section is the primary place to check before starting your next task."
    )


# =============================================================================
# COMPLETED
# =============================================================================

elif page == "Completed Work":

    st.markdown(
        '<div class="section-title">✓ COMPLETED WORK</div>',
        unsafe_allow_html=True,
    )

    completed = [
        item for item in ROADMAP
        if item["status"] == "COMPLETE"
    ]

    for item in completed:

        st.markdown(
            f"""
            <div class="card">

            <span class="status-complete">
            ✓ COMPLETE
            </span>

            <br><br>

            <div class="step-number">
            {item["id"]}
            </div>

            <div class="step-title">
            {item["title"]}
            </div>

            <br>

            {item["description"]}

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# REMAINING
# =============================================================================

elif page == "Remaining Work":

    st.markdown(
        '<div class="section-title">🔥 REMAINING WORK</div>',
        unsafe_allow_html=True,
    )

    remaining = [
        item for item in ROADMAP
        if item["status"] != "COMPLETE"
    ]

    for item in remaining:

        label = (
            "⚡ NEXT"
            if item["status"] == "NEXT"
            else "○ PLANNED"
        )

        st.markdown(
            f"""
            <div class="card">

            <b>{label}</b>

            <br><br>

            <div class="step-number">
            {item["id"]}
            </div>

            <div class="step-title">
            {item["title"]}
            </div>

            <br>

            {item["description"]}

            <div class="owner-action">
            <b>OWNER ACTION</b><br>
            {item["owner"]}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# EVENTS
# =============================================================================

elif page == "Project Events":

    st.markdown(
        '<div class="section-title">📜 PROJECT EVENTS — PROJECT HISTORY</div>',
        unsafe_allow_html=True,
    )

    if not events:

        st.info("No monitoring events have been recorded yet.")

    else:

        for event in events[:50]:

            event_type = event.get(
                "event_type",
                "EVENT",
            )

            message = event.get(
                "message",
                "",
            )

            timestamp = event.get(
                "timestamp",
                event.get("time", ""),
            )

            st.markdown(
                f"""
                <div class="event-card">

                <b style="color:#d4af37;">
                {event_type}
                </b>

                <br>

                {message}

                <br>

                <small style="color:#999;">
                {timestamp}
                </small>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# PROJECT INFORMATION
# =============================================================================

elif page == "Project Information":

    st.markdown(
        '<div class="section-title">📊 PROJECT INFORMATION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card">

        <b>Project</b><br>
        Einstein AI V2

        <br><br>

        <b>Architecture Goal</b><br>
        A modular AI research and reasoning platform inspired by
        Einstein's documented scientific reasoning patterns.

        <br><br>

        <b>Important Design Principle</b><br>
        The project does NOT claim to reconstruct Einstein's biological brain.
        The goal is to model useful reasoning patterns through computational
        systems, knowledge, memory, experimentation and evaluation.

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">🔗 VERSION CONTROL</div>',
        unsafe_allow_html=True,
    )

    st.write(
        f"**Branch:** {git.get('branch') or 'Unknown'}"
    )

    st.write(
        f"**Latest commit:** {git.get('commit') or 'Unknown'}"
    )

    if git.get("status"):
        st.warning(
            "There are local working-tree changes."
        )
    else:
        st.success(
            "Working tree appears clean."
        )


# =============================================================================
# FOOTER
# =============================================================================

st.markdown('<div class="blade-line"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        text-align:center;
        color:#d4af37;
        padding:20px;
        letter-spacing:0.12em;
    ">
        ⚔️ EINSTEIN AI V2 • OWNER COMMAND CENTER
        <br>
        <small style="color:#888;">
        PLAN • BUILD • VALIDATE • ADVANCE
        </small>
    </div>
    """,
    unsafe_allow_html=True,
)
