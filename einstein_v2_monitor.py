
"""
===============================================================================
EINSTEIN AI V2 — OWNER MONITORING COMMAND CENTER
===============================================================================

Owner-only Streamlit monitoring interface.

Design:
    - Landscape-first desktop command center
    - Dark Einstein AI interface
    - Bleach / Soul-Reaper inspired visual language
    - Custom CSS
    - Cognitive architecture monitoring
    - Expert network monitoring
    - Memory monitoring
    - Research monitoring
    - Engineering monitoring
    - Audit monitoring
    - System integrity

This file is UI-safe and can be connected to the existing Einstein AI V2
monitoring backend without replacing the backend architecture.
===============================================================================
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Einstein AI V2 | Owner Command Center",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

AUDIT_DIR = PROJECT_ROOT / "audit"
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

PROJECT_LOG = LOG_DIR / "project_log.md"
AUDIT_LOG = AUDIT_DIR / "audit_events.jsonl"

AUDIT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


# =============================================================================
# SESSION STATE
# =============================================================================

if "page" not in st.session_state:
    st.session_state.page = "Command Center"

if "monitoring" not in st.session_state:
    st.session_state.monitoring = True

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown(
    """
<style>

/* ========================================================================== */
/* GLOBAL                                                                     */
/* ========================================================================== */

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 80% 10%,
            rgba(255,255,255,0.055),
            transparent 28%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(255,255,255,0.025),
            transparent 30%
        ),
        #050505;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1900px;
    padding-top: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 3rem;
}


/* ========================================================================== */
/* SIDEBAR                                                                    */
/* ========================================================================== */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #090909,
            #111111 50%,
            #070707
        ) !important;

    border-right: 1px solid rgba(255,255,255,0.08);
}

.sidebar-logo {
    text-align: center;
    padding: 12px 5px 25px 5px;
}

.sidebar-sword {
    font-size: 45px;
    line-height: 1;
    filter: drop-shadow(
        0 0 12px rgba(255,255,255,0.25)
    );
}

.sidebar-title {
    color: #f2f2f2;
    font-size: 17px;
    font-weight: 900;
    letter-spacing: 3px;
    margin-top: 12px;
}

.sidebar-subtitle {
    color: #686868;
    font-size: 9px;
    letter-spacing: 2px;
    margin-top: 5px;
}


/* ========================================================================== */
/* COMMAND HEADER                                                             */
/* ========================================================================== */

.command-header {
    position: relative;
    overflow: hidden;

    min-height: 155px;

    padding: 27px 30px;

    border-radius: 18px;

    border: 1px solid rgba(255,255,255,0.11);

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.075),
            rgba(255,255,255,0.015)
        );

    box-shadow:
        0 18px 50px rgba(0,0,0,0.38);
}

.command-header:before {
    content: "";

    position: absolute;

    width: 260px;
    height: 260px;

    right: -80px;
    top: -120px;

    border-radius: 50%;

    border:
        1px solid rgba(255,255,255,0.08);
}

.command-header:after {
    content: "";

    position: absolute;

    width: 170px;
    height: 170px;

    right: -35px;
    top: -75px;

    border-radius: 50%;

    border:
        1px solid rgba(255,255,255,0.055);
}

.kicker {
    color: #777;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 4px;
}

.main-title {
    color: #f4f4f4;

    font-size: 35px;

    font-weight: 950;

    letter-spacing: 2px;

    margin-top: 7px;
}

.description {
    color: #898989;

    font-size: 12px;

    max-width: 850px;

    margin-top: 7px;
}


/* ========================================================================== */
/* ONLINE STATUS                                                              */
/* ========================================================================== */

.online {
    display: inline-flex;

    align-items: center;

    gap: 8px;

    margin-top: 17px;

    padding: 7px 13px;

    border-radius: 100px;

    border:
        1px solid rgba(255,255,255,0.1);

    background:
        rgba(255,255,255,0.035);

    color: #cfcfcf;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1.5px;
}

.online-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #eeeeee;

    box-shadow:
        0 0 12px rgba(255,255,255,0.7);

    animation:
        pulse 1.8s infinite;
}

@keyframes pulse {

    0%,100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.4;
        transform: scale(0.7);
    }

}


/* ========================================================================== */
/* METRIC CARDS                                                               */
/* ========================================================================== */

.metric {
    padding: 19px;

    min-height: 125px;

    border-radius: 15px;

    border:
        1px solid rgba(255,255,255,0.08);

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.055),
            rgba(255,255,255,0.012)
        );

    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}

.metric:hover {
    transform: translateY(-3px);

    border-color:
        rgba(255,255,255,0.2);
}

.metric-label {
    color: #707070;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 2px;
}

.metric-value {
    color: #eeeeee;

    font-size: 29px;

    font-weight: 950;

    margin-top: 8px;
}

.metric-detail {
    color: #666;

    font-size: 10px;

    margin-top: 4px;
}


/* ========================================================================== */
/* PANELS                                                                     */
/* ========================================================================== */

.panel {
    padding: 20px;

    border-radius: 16px;

    border:
        1px solid rgba(255,255,255,0.075);

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.045),
            rgba(255,255,255,0.012)
        );

    margin-bottom: 16px;
}

.panel-title {
    color: #e7e7e7;

    font-size: 11px;

    font-weight: 900;

    letter-spacing: 2px;

    margin-bottom: 7px;
}

.panel-description {
    color: #666;

    font-size: 10px;

    margin-bottom: 16px;
}


/* ========================================================================== */
/* REIATSU                                                                     */
/* ========================================================================== */

.reiatsu-box {
    text-align: center;

    padding: 15px 10px;
}

.reiatsu-ring {
    width: 125px;
    height: 125px;

    margin:
        5px auto 15px;

    border-radius: 50%;

    border:
        1px solid rgba(255,255,255,0.17);

    display: flex;

    align-items: center;

    justify-content: center;

    box-shadow:
        0 0 35px rgba(255,255,255,0.055),
        inset 0 0 35px rgba(255,255,255,0.035);

    animation:
        reiatsu 3s ease-in-out infinite;
}

@keyframes reiatsu {

    0%,100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.035);
    }

}

.reiatsu-number {
    font-size: 30px;

    font-weight: 950;

    color: #eeeeee;
}

.reiatsu-label {
    color: #666;

    font-size: 8px;

    letter-spacing: 3px;
}


/* ========================================================================== */
/* MODULE CARDS                                                               */
/* ========================================================================== */

.module {
    padding: 13px;

    margin-bottom: 8px;

    border-radius: 10px;

    border:
        1px solid rgba(255,255,255,0.055);

    background:
        rgba(255,255,255,0.018);

    transition:
        background 0.2s ease,
        border-color 0.2s ease;
}

.module:hover {
    background:
        rgba(255,255,255,0.045);

    border-color:
        rgba(255,255,255,0.13);
}

.module-name {
    color: #d8d8d8;

    font-size: 11px;

    font-weight: 750;
}

.module-info {
    color: #666;

    font-size: 9px;

    margin-top: 3px;
}


/* ========================================================================== */
/* PROGRESS                                                                   */
/* ========================================================================== */

.progress-container {
    width: 100%;

    height: 6px;

    background:
        rgba(255,255,255,0.06);

    border-radius: 50px;

    overflow: hidden;

    margin-top: 9px;
}

.progress-bar {
    height: 100%;

    border-radius: 50px;

    background:
        linear-gradient(
            90deg,
            #555,
            #eeeeee
        );
}


/* ========================================================================== */
/* TERMINAL                                                                   */
/* ========================================================================== */

.terminal {
    background: #020202;

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 12px;

    padding: 16px;

    min-height: 190px;

    font-family:
        "Courier New",
        monospace;

    font-size: 10px;

    color: #a9a9a9;

    overflow-y: auto;
}

.terminal-line {
    margin-bottom: 8px;
}

.terminal-prefix {
    color: #666;
}


/* ========================================================================== */
/* AUDIT ROWS                                                                 */
/* ========================================================================== */

.audit-row {
    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 12px 2px;

    border-bottom:
        1px solid rgba(255,255,255,0.045);
}

.audit-name {
    color: #cfcfcf;

    font-size: 10px;

    font-weight: 700;
}

.audit-time {
    color: #555;

    font-size: 9px;
}


/* ========================================================================== */
/* STREAMLIT BUTTONS                                                           */
/* ========================================================================== */

.stButton > button {

    width: 100%;

    min-height: 38px;

    border-radius: 9px;

    border:
        1px solid rgba(255,255,255,0.1);

    background:
        rgba(255,255,255,0.04);

    color: #dedede;

    font-weight: 800;

    font-size: 10px;

    letter-spacing: 0.7px;

    transition: 0.2s ease;
}

.stButton > button:hover {

    background:
        rgba(255,255,255,0.09);

    border-color:
        rgba(255,255,255,0.25);

    transform:
        translateY(-1px);
}


/* ========================================================================== */
/* DIVIDER                                                                    */
/* ========================================================================== */

hr {
    border-color:
        rgba(255,255,255,0.07);
}


/* ========================================================================== */
/* MOBILE FALLBACK                                                            */
/* ========================================================================== */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        font-size: 24px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# HELPERS
# =============================================================================

def safe_text(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001, S110
        pass

    return ""


def file_count() -> int:
    try:
        return sum(
            1
            for p in PROJECT_ROOT.rglob("*")
            if p.is_file()
            and ".git" not in p.parts
            and "__pycache__" not in p.parts
        )
    except Exception:  # noqa: BLE001
        return 0


def line_count(path: Path) -> int:
    try:
        return len(safe_text(path).splitlines())
    except Exception:  # noqa: BLE001
        return 0


def audit_events() -> list[dict]:
    if not AUDIT_LOG.exists():
        return []

    events = []

    try:
        lines = AUDIT_LOG.read_text(
            encoding="utf-8"
        ).splitlines()

        for line in lines[-15:]:

            try:
                events.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:

                events.append(
                    {
                        "event": line,
                        "status": "INFO",
                        "timestamp": "",
                    }
                )

    except Exception:  # noqa: BLE001, S110
        pass

    return list(reversed(events))


# =============================================================================
# ARCHITECTURE REGISTRY
# =============================================================================

COGNITIVE_MODULES = [
    "Reasoning Engine",
    "Thought Experiments",
    "Analogy Engine",
    "Hypothesis Generator",
    "Critical Thinking",
    "Mathematical Reasoning",
    "Scientific Reasoning",
    "Causal Reasoning",
    "Memory Retrieval",
    "Semantic Memory",
    "Episodic Memory",
    "Working Memory",
    "Self Evaluation",
    "Uncertainty Engine",
    "Research Planner",
    "Experiment Planner",
    "Creative Synthesis",
    "Problem Decomposition",
    "Perspective Engine",
    "Final Synthesis",
]

EXPERTS = [
    "Physics Expert",
    "Mathematics Expert",
    "Scientific Research Expert",
    "Critical Reasoning Expert",
    "Creative Analogy Expert",
    "Computation Expert",
    "Engineering Expert",
    "Research Literature Expert",
    "Hypothesis Expert",
    "Synthesis Expert",
]

MEMORY_SYSTEMS = [
    "Working Memory",
    "Semantic Memory",
    "Episodic Memory",
    "Procedural Memory",
    "Research Memory",
    "Reasoning Trace Memory",
]


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-sword">
                ⚔
            </div>

            <div class="sidebar-title">
                EINSTEIN AI V2
            </div>

            <div class="sidebar-subtitle">
                SOUL SOCIETY COMMAND SYSTEM
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = [
        "Command Center",
        "Cognitive Core",
        "Expert Network",
        "Memory System",
        "Research",
        "Engineering Monitor",
        "Audit Log",
        "System Integrity",
    ]

    st.session_state.page = st.radio(
        "COMMAND",
        pages,
        index=pages.index(
            st.session_state.page
        ),
    )

    st.divider()

    st.session_state.monitoring = st.toggle(
        "Live Monitoring",
        value=st.session_state.monitoring,
    )

    st.session_state.auto_refresh = st.toggle(
        "Auto Refresh",
        value=st.session_state.auto_refresh,
    )

    st.divider()

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#555;
            font-size:9px;
            letter-spacing:2px;
            line-height:1.8;
        ">
            OWNER ACCESS<br>
            COMMAND AUTHORITY<br>
            MONITORING BRANCH
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# GLOBAL HEADER
# =============================================================================

st.markdown(
    """
    <div class="command-header">

        <div class="kicker">
            OWNER // EINSTEIN AI V2 // MONITORING
        </div>

        <div class="main-title">
            ⚔ EINSTEIN COMMAND CENTER
        </div>

        <div class="description">
            Advanced monitoring interface for cognitive architecture,
            reasoning systems, research operations, engineering progress
            and system integrity.
        </div>

        <div class="online">
            <span class="online-dot"></span>
            SYSTEM ONLINE
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# METRICS
# =============================================================================

cols = st.columns(5)

metric_data = [
    (
        "COGNITIVE MODULES",
        len(COGNITIVE_MODULES),
        "Registered modules",
    ),
    (
        "EXPERT NODES",
        len(EXPERTS),
        "MoE specialists",
    ),
    (
        "MEMORY SYSTEMS",
        len(MEMORY_SYSTEMS),
        "Memory architecture",
    ),
    (
        "PROJECT FILES",
        file_count(),
        "Tracked artifacts",
    ),
    (
        "AUDIT EVENTS",
        len(audit_events()),
        "Recorded events",
    ),
]

for col, (label, value, detail) in zip(
    cols,
    metric_data,
):

    with col:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-label">
                    {label}
                </div>

                <div class="metric-value">
                    {value}
                </div>

                <div class="metric-detail">
                    {detail}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# COMMAND CENTER
# =============================================================================

if st.session_state.page == "Command Center":

    left, middle, right = st.columns(
        [1.0, 1.85, 1.0]
    )

    # -------------------------------------------------------------------------
    # LEFT
    # -------------------------------------------------------------------------

    with left:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    ⚡ REIATSU MONITOR
                </div>

                <div class="panel-description">
                    Cognitive system activity
                </div>

                <div class="reiatsu-box">

                    <div class="reiatsu-ring">

                        <div class="reiatsu-number">
                            87%
                        </div>

                    </div>

                    <div class="reiatsu-label">
                        COGNITIVE ACTIVITY
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    SYSTEM SIGNALS
                </div>

                <div class="module">
                    <div class="module-name">
                        ● Cognitive Core
                    </div>
                    <div class="module-info">
                        Operational
                    </div>
                </div>

                <div class="module">
                    <div class="module-name">
                        ● Memory Layer
                    </div>
                    <div class="module-info">
                        Connected
                    </div>
                </div>

                <div class="module">
                    <div class="module-name">
                        ● Expert Router
                    </div>
                    <div class="module-info">
                        Ready
                    </div>
                </div>

                <div class="module">
                    <div class="module-name">
                        ● Research Layer
                    </div>
                    <div class="module-info">
                        Monitoring
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # -------------------------------------------------------------------------
    # MIDDLE
    # -------------------------------------------------------------------------

    with middle:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    🧠 COGNITIVE CORE
                </div>

                <div class="panel-description">
                    Current reasoning architecture activity
                </div>
            """,
            unsafe_allow_html=True,
        )

        progress = {
            "Reasoning Engine": 91,
            "Thought Experiments": 76,
            "Analogy Engine": 69,
            "Hypothesis Generator": 84,
            "Critical Thinking": 88,
            "Mathematical Reasoning": 73,
            "Scientific Reasoning": 82,
            "Self Evaluation": 61,
        }

        for name, value in progress.items():

            st.markdown(
                f"""
                <div style="margin-bottom:14px;">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        font-size:10px;
                        color:#bdbdbd;
                    ">

                        <span>
                            {name}
                        </span>

                        <span style="color:#666;">
                            {value}%
                        </span>

                    </div>

                    <div class="progress-container">

                        <div
                            class="progress-bar"
                            style="width:{value}%;">
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    ⚔ ACTIVE OPERATION
                </div>

                <div style="
                    font-size:18px;
                    font-weight:900;
                    color:#e6e6e6;
                ">
                    Cognitive Architecture Integration
                </div>

                <div style="
                    color:#666;
                    font-size:10px;
                    margin-top:7px;
                ">
                    Monitoring cognitive modules, reasoning pipelines,
                    memory interfaces and expert routing.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # -------------------------------------------------------------------------
    # RIGHT
    # -------------------------------------------------------------------------

    with right:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    🛡 SYSTEM INTEGRITY
                </div>

                <div class="metric-value">
                    PASS
                </div>

                <div class="metric-detail">
                    Core monitoring state
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        log_exists = PROJECT_LOG.exists()

        st.markdown(
            f"""
            <div class="panel">

                <div class="panel-title">
                    📜 PROJECT LOG
                </div>

                <div class="metric-value">
                    {"READY" if log_exists else "CHECK"}
                </div>

                <div class="metric-detail">
                    {line_count(PROJECT_LOG)} lines recorded
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "↻ REFRESH SYSTEM",
            key="command_refresh",
        ):
            st.rerun()


# =============================================================================
# COGNITIVE CORE
# =============================================================================

elif st.session_state.page == "Cognitive Core":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                🧠 COGNITIVE ARCHITECTURE
            </div>

            <div class="panel-description">
                Einstein AI V2 reasoning and cognitive module registry.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    for index, module in enumerate(
        COGNITIVE_MODULES
    ):

        with columns[index % 4]:

            st.markdown(
                f"""
                <div class="module">

                    <div class="module-name">
                        {module}
                    </div>

                    <div class="module-info">
                        STATUS: READY
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# EXPERT NETWORK
# =============================================================================

elif st.session_state.page == "Expert Network":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                ⚡ MIXTURE OF EXPERTS
            </div>

            <div class="panel-description">
                Specialist reasoning nodes available to the synthesis layer.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(2)

    for index, expert in enumerate(EXPERTS):

        with columns[index % 2]:

            st.markdown(
                f"""
                <div class="module">

                    <div class="module-name">
                        ⚔ {expert}
                    </div>

                    <div class="module-info">
                        SPECIALIST NODE — ONLINE
                    </div>

                    <div class="progress-container">

                        <div
                            class="progress-bar"
                            style="width:{70 + (index * 2) % 25}%;">
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# MEMORY SYSTEM
# =============================================================================

elif st.session_state.page == "Memory System":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                🌀 MEMORY ARCHITECTURE
            </div>

            <div class="panel-description">
                Cognitive memory subsystems.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3)

    for index, memory in enumerate(
        MEMORY_SYSTEMS
    ):

        with columns[index % 3]:

            st.markdown(
                f"""
                <div class="metric">

                    <div class="metric-label">
                        MEMORY NODE
                    </div>

                    <div style="
                        color:#ddd;
                        font-size:17px;
                        font-weight:850;
                        margin-top:9px;
                    ">
                        {memory}
                    </div>

                    <div class="metric-detail">
                        ACTIVE
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# RESEARCH
# =============================================================================

elif st.session_state.page == "Research":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                🔬 RESEARCH PIPELINE
            </div>

            <div class="panel-description">
                Question → research → evidence → hypothesis → testing →
                critique → revision → synthesis.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    research_stages = [
        ("01", "Question", 100),
        ("02", "Research", 82),
        ("03", "Evidence", 76),
        ("04", "Hypothesis", 68),
        ("05", "Experiment", 55),
        ("06", "Critique", 42),
        ("07", "Revision", 31),
        ("08", "Synthesis", 24),
    ]

    for number, name, value in research_stages:

        c1, c2, c3 = st.columns(
            [0.08, 0.25, 1]
        )

        with c1:
            st.markdown(
                f"""
                <div style="
                    color:#555;
                    font-size:10px;
                    padding-top:5px;
                ">
                    {number}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div style="
                    color:#ccc;
                    font-size:11px;
                    font-weight:700;
                    padding-top:5px;
                ">
                    {name}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.progress(value / 100)


# =============================================================================
# ENGINEERING MONITOR
# =============================================================================

elif st.session_state.page == "Engineering Monitor":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                💻 ENGINEERING MONITOR
            </div>

            <div class="panel-description">
                Einstein AI V2 engineering, testing and project automation.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    engineering = [
        ("RUFF", "PASS", "Static analysis"),
        ("PYTEST", "PASS", "Automated tests"),
        ("PROJECT LOG", "AUTO", "Engineering history"),
    ]

    for col, (name, value, detail) in zip(
        [c1, c2, c3],
        engineering,
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric">

                    <div class="metric-label">
                        {name}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>

                    <div class="metric-detail">
                        {detail}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                TERMINAL
            </div>

            <div class="terminal">

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [SYSTEM]
                    </span>
                    Einstein AI V2 monitoring initialized.
                </div>

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [COGNITIVE]
                    </span>
                    Cognitive architecture registry loaded.
                </div>

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [MEMORY]
                    </span>
                    Memory subsystem detected.
                </div>

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [EXPERT]
                    </span>
                    Expert network registry detected.
                </div>

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [TEST]
                    </span>
                    Testing pipeline ready.
                </div>

                <div class="terminal-line">
                    <span class="terminal-prefix">
                        [BRANCH]
                    </span>
                    Monitoring branch interface active.
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# AUDIT LOG
# =============================================================================

elif st.session_state.page == "Audit Log":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                📜 AUDIT LOG
            </div>

            <div class="panel-description">
                Engineering and monitoring events.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    events = audit_events()

    if not events:

        st.info(
            "No audit events have been recorded yet."
        )

    else:

        for event in events:

            name = (
                event.get("event")
                or event.get("action")
                or "Unknown event"
            )

            status = (
                event.get("status")
                or "INFO"
            )

            timestamp = (
                event.get("timestamp")
                or event.get("time")
                or ""
            )

            st.markdown(
                f"""
                <div class="audit-row">

                    <div>

                        <div class="audit-name">
                            {status} — {name}
                        </div>

                        <div class="audit-time">
                            {timestamp}
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# SYSTEM INTEGRITY
# =============================================================================

elif st.session_state.page == "System Integrity":

    st.markdown(
        """
        <div class="panel">

            <div class="panel-title">
                🛡 SYSTEM INTEGRITY
            </div>

            <div class="panel-description">
                Einstein AI V2 project health checks.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    checks = [
        ("Project root", PROJECT_ROOT.exists()),
        ("Audit directory", AUDIT_DIR.exists()),
        ("Log directory", LOG_DIR.exists()),
        ("Data directory", DATA_DIR.exists()),
        ("README", (PROJECT_ROOT / "README.md").exists()),
        (
            "requirements.txt",
            (PROJECT_ROOT / "requirements.txt").exists(),
        ),
        (
            "einstein_v2.py",
            (PROJECT_ROOT / "einstein_v2.py").exists(),
        ),
        ("Project log", PROJECT_LOG.exists()),
    ]

    for name, passed in checks:

        status = "PASS" if passed else "CHECK"

        st.markdown(
            f"""
            <div class="audit-row">

                <div class="audit-name">
                    {name}
                </div>

                <div style="
                    color:#bbb;
                    font-size:9px;
                    font-weight:900;
                    letter-spacing:1px;
                ">
                    {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# FOOTER
# =============================================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:35px;
        padding:20px;
        color:#4d4d4d;
        font-size:8px;
        letter-spacing:2px;
        line-height:2;
    ">
        EINSTEIN AI V2
        •
        OWNER COMMAND CENTER
        •
        MONITORING BRANCH
        <br>
        THINK DEEPLY • QUESTION ASSUMPTIONS • BUILD • TEST • REVISE
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# OPTIONAL AUTO REFRESH
# =============================================================================

if st.session_state.auto_refresh:

    time.sleep(5)

    st.rerun()
