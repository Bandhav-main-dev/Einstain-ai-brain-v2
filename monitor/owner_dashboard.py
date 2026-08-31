import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# =============================================================================
# EINSTEIN AI V2 — OWNER COMMAND CENTER
# BLEACH × F1 INSPIRED / STREAMLIT NATIVE
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTROL_FILE = PROJECT_ROOT / "project_control.json"
ENGINE_FILE = PROJECT_ROOT / "monitor" / "progress_engine.py"


# =============================================================================
# PAGE
# =============================================================================

st.set_page_config(
    page_title="Einstein AI V2 — Owner Command Center",
    page_icon="🏎️",
    layout="wide",
)


# =============================================================================
# EINSTEIN AI V2 — V4 VISUAL STYLE LAYER
# BLEACH × F1 INSPIRED
# =============================================================================

st.markdown(
    """
    <style>

    /* ================================================================
       GLOBAL
       ================================================================ */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(20, 70, 150, 0.18),
                transparent 32%
            ),
            radial-gradient(
                circle at bottom left,
                rgba(180, 0, 0, 0.15),
                transparent 30%
            ),
            #050505;
        color: #ffffff;
    }


    /* ================================================================
       MAIN CONTENT
       ================================================================ */

    .main .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ================================================================
       HEADINGS
       ================================================================ */

    h1 {
        font-weight: 900 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase;
        text-shadow:
            0 0 12px rgba(220, 0, 0, 0.35);
    }

    h2 {
        font-weight: 850 !important;
        letter-spacing: 0.025em;
    }

    h3 {
        font-weight: 750 !important;
    }


    /* ================================================================
       METRIC CARDS
       ================================================================ */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(20, 20, 20, 0.96),
                rgba(7, 7, 7, 0.96)
            );

        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #d90404;

        border-radius: 14px;

        padding: 1rem;

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.35);

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);

        border-left-color: #ffd700;

        box-shadow:
            0 10px 35px rgba(210, 0, 0, 0.18);
    }


    /* ================================================================
       PROGRESS BARS
       ================================================================ */

    div[data-testid="stProgressBar"] {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        overflow: hidden;
    }

    div[data-testid="stProgressBar"] > div {
        border-radius: 999px;
    }


    /* ================================================================
       EXPANDERS
       ================================================================ */

    div[data-testid="stExpander"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 15, 15, 0.96),
                rgba(5, 5, 5, 0.96)
            );

        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;

        margin-bottom: 0.6rem;

        transition:
            border-color 0.2s ease,
            transform 0.2s ease;
    }

    div[data-testid="stExpander"]:hover {
        border-color: rgba(220, 0, 0, 0.55);
    }


    /* ================================================================
       BUTTONS
       ================================================================ */

    .stButton > button {
        border-radius: 10px;

        border: 1px solid rgba(255, 255, 255, 0.14);

        background:
            linear-gradient(
                135deg,
                #111111,
                #1b1b1b
            );

        color: #ffffff;

        font-weight: 750;

        min-height: 44px;

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        border-color: #d90404;

        box-shadow:
            0 7px 25px rgba(220, 0, 0, 0.25);
    }

    .stButton > button:active {
        transform: translateY(0);
    }


    /* ================================================================
       INPUTS
       ================================================================ */

    div[data-baseweb="input"] {
        background: #0b0b0b;
    }

    div[data-baseweb="select"] {
        background: #0b0b0b;
    }


    /* ================================================================
       ALERTS / STATUS
       ================================================================ */

    div[data-testid="stAlert"] {
        border-radius: 12px;
        border-left-width: 4px;
    }


    /* ================================================================
       DIVIDERS
       ================================================================ */

    hr {
        border: 0;
        height: 1px;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(220, 0, 0, 0.65),
                rgba(0, 100, 220, 0.45),
                rgba(255, 215, 0, 0.55),
                transparent
            );

        margin: 1.5rem 0;
    }


    /* ================================================================
       CAPTIONS
       ================================================================ */

    .stCaption {
        color: rgba(255, 255, 255, 0.62);
    }


    /* ================================================================
       COMMAND CENTER ANIMATION
       ================================================================ */

    @keyframes racePulse {

        0% {
            box-shadow:
                0 0 0 rgba(220, 0, 0, 0);
        }

        50% {
            box-shadow:
                0 0 22px rgba(220, 0, 0, 0.15);
        }

        100% {
            box-shadow:
                0 0 0 rgba(220, 0, 0, 0);
        }
    }


    /* ================================================================
       ACTIVE OWNER ACCESS
       ================================================================ */

    div[data-testid="stAlert"] {
        animation:
            racePulse 3.5s ease-in-out infinite;
    }


    /* ================================================================
       MOBILE
       ================================================================ */

    @media (max-width: 768px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.7rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        div[data-testid="stMetric"] {
            margin-bottom: 0.6rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)




# =============================================================================
# HELPERS
# =============================================================================

def load_control() -> dict:
    """Load project control JSON."""

    with CONTROL_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_control(
    control: dict,
) -> None:
    """Save project control JSON."""

    control.setdefault(
        "project",
        {},
    )

    control["project"]["last_updated"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    with CONTROL_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            control,
            file,
            indent=2,
        )


def run_progress_engine() -> tuple[
    bool,
    str,
]:
    """Run automatic project monitoring."""

    result = subprocess.run(
        [
            sys.executable,
            str(ENGINE_FILE),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = (
        result.stdout
        + "\n"
        + result.stderr
    ).strip()

    return (
        result.returncode == 0,
        output,
    )


def calculate_overall_progress(
    control: dict,
) -> int:
    """Calculate weighted roadmap progress."""

    steps = control.get(
        "steps",
        [],
    )

    total_weight = 0.0
    weighted_score = 0.0

    for step in steps:

        progress = float(
            step.get(
                "progress",
                0,
            )
        )

        weight = float(
            step.get(
                "weight",
                1,
            )
        )

        total_weight += weight
        weighted_score += (
            progress * weight
        )

    if total_weight <= 0:
        return 0

    return round(
        weighted_score
        / total_weight
    )


def progress_label(
    progress: int,
) -> str:

    if progress >= 100:
        return "COMPLETED"

    if progress > 0:
        return "IN PROGRESS"

    return "PENDING"


def status_icon(
    progress: int,
) -> str:

    if progress >= 100:
        return "🟢"

    if progress > 0:
        return "🟡"

    return "⚪"


def get_git_value(
    args: list[str],
) -> str:

    try:

        result = subprocess.run(
            [
                "git",
                *args,
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return "UNKNOWN"

        return result.stdout.strip()

    except OSError:
        return "UNKNOWN"


def get_git_branch() -> str:
    return get_git_value(
        [
            "branch",
            "--show-current",
        ]
    )


def get_git_status() -> str:

    value = get_git_value(
        [
            "status",
            "--short",
        ]
    )

    if not value:
        return "CLEAN"

    return "CHANGES"


def get_health(
    control: dict,
) -> str:

    monitoring = control.get(
        "monitoring",
        {},
    )

    return monitoring.get(
        "status",
        "UNKNOWN",
    ).upper()


def get_next_step(
    steps: list[dict],
) -> dict | None:

    for step in steps:

        if step.get(
            "progress",
            0,
        ) < 100:

            return step

    return None


# =============================================================================
# LOAD STATE
# =============================================================================

control = load_control()

steps = control.get(
    "steps",
    [],
)

progress = control.get(
    "progress",
    {},
)

overall = calculate_overall_progress(
    control
)

progress["overall"] = overall

control["progress"] = progress


# =============================================================================
# HEADER
# =============================================================================



# =============================================================================
# EINSTEIN AI V2 — OWNER AUTHORIZATION
# =============================================================================

def get_owner_credentials() -> tuple[str, str]:
    """Read owner credentials from Streamlit secrets."""

    try:
        username = str(
            st.secrets.get(
                "owner_username",
                "",
            )
        )

        password = str(
            st.secrets.get(
                "owner_password",
                "",
            )
        )

        return username, password

    except (KeyError, TypeError):
        return "", ""


def verify_owner(
    username: str,
    password: str,
) -> bool:
    """Verify supplied owner credentials."""

    configured_username, configured_password = (
        get_owner_credentials()
    )

    if not configured_username:
        return False

    if not configured_password:
        return False

    return (
        username == configured_username
        and password == configured_password
    )


def add_audit_event(
    control: dict,
    action: str,
    actor: str,
) -> None:
    """Record an owner action."""

    audit = control.setdefault(
        "audit",
        {},
    )

    events = audit.setdefault(
        "events",
        [],
    )

    events.append(
        {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "actor": actor,
            "action": action,
        }
    )

    audit["events"] = events[-100:]


def owner_authorized() -> bool:
    """Return whether the current Streamlit session is authorized."""

    return bool(
        st.session_state.get(
            "owner_authenticated",
            False,
        )
    )


# =============================================================================
# OWNER SESSION
# =============================================================================

if "owner_authenticated" not in st.session_state:
    st.session_state.owner_authenticated = False

if "owner_username" not in st.session_state:
    st.session_state.owner_username = ""


# =============================================================================
# OWNER ACCESS CONTROL
# =============================================================================

st.divider()

st.subheader(
    "🔐 OWNER ACCESS CONTROL"
)

auth_col1, auth_col2 = st.columns(2)


with auth_col1:

    if owner_authorized():

        st.success(
            "🔓 OWNER ACCESS ACTIVE"
        )

        st.caption(
            "Write controls are enabled."
        )

        if st.button(
            "🔒 Lock Owner Session",
            use_container_width=True,
        ):

            control = load_control()

            add_audit_event(
                control,
                "OWNER_SESSION_LOCKED",
                st.session_state.owner_username,
            )

            save_control(control)

            st.session_state.owner_authenticated = False
            st.session_state.owner_username = ""

            st.rerun()

    else:

        st.info(
            "👁️ VIEWER MODE"
        )

        st.caption(
            "Read-only monitoring access."
        )


with auth_col2:

    if not owner_authorized():

        login_username = st.text_input(
            "Owner username",
        )

        login_password = st.text_input(
            "Owner password",
            type="password",
        )

        if st.button(
            "🔑 Authenticate Owner",
            use_container_width=True,
        ):

            if verify_owner(
                login_username,
                login_password,
            ):

                st.session_state.owner_authenticated = True

                st.session_state.owner_username = (
                    login_username
                )

                control = load_control()

                add_audit_event(
                    control,
                    "OWNER_SESSION_AUTHENTICATED",
                    login_username,
                )

                save_control(control)

                st.success(
                    "Owner authentication successful."
                )

                st.rerun()

            else:

                st.error(
                    "Authentication failed."
                )


if owner_authorized():

    st.success(
        "🔓 Authorized owner controls available."
    )

else:

    st.warning(
        "🔒 Owner authorization required for write actions."
    )


st.title(
    "🏎️ EINSTEIN AI V2"
)

st.subheader(
    "⚔️ OWNER COMMAND CENTER"
)

st.caption(
    "BLEACH × F1 INSPIRED • "
    "AUTOMATIC PROJECT MONITORING"
)


# =============================================================================
# TELEMETRY
# =============================================================================

st.divider()

st.subheader(
    "🏁 LIVE PROJECT TELEMETRY"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Overall Progress",
        f"{overall}%",
    )

with col2:
    completed = sum(
        1
        for step in steps
        if step.get(
            "progress",
            0,
        ) >= 100
    )

    st.metric(
        "Stages Complete",
        f"{completed}/{len(steps)}",
    )

with col3:
    health = get_health(
        control
    )

    st.metric(
        "System Health",
        health,
    )

with col4:
    branch = get_git_branch()

    st.metric(
        "Git Branch",
        branch or "UNKNOWN",
    )


st.progress(
    overall / 100,
)


# =============================================================================
# CONTROL PANEL
# =============================================================================

st.divider()

st.subheader(
    "🎛️ RACE CONTROL"
)

control_col1, control_col2 = st.columns(2)

with control_col1:

    if owner_authorized() and st.button(
        "🔄 Run Automatic Progress Scan",
        use_container_width=True,
    ):

        with st.spinner(
            "Running Einstein AI V2 monitoring engine..."
        ):

            success, output = (
                run_progress_engine()
            )

        if success:

            st.success(
                "Automatic monitoring scan completed."
            )

            st.code(
                output,
                language="text",
            )

            st.rerun()

        else:

            st.error(
                "Monitoring scan failed."
            )

            st.code(
                output,
                language="text",
            )


with control_col2:

    if st.button(
        "📡 Refresh Command Center",
        use_container_width=True,
    ):

        st.rerun()


# =============================================================================
# ROADMAP
# =============================================================================

st.divider()

st.subheader(
    "⚔️ ZANPAKUTŌ ROADMAP"
)

for index, step in enumerate(
    steps,
    start=1,
):

    step_id = step.get(
        "id",
        f"STEP-{index}",
    )

    name = step.get(
        "name",
        "Unnamed Stage",
    )

    step_progress = int(
        step.get(
            "progress",
            0,
        )
    )

    weight = step.get(
        "weight",
        1,
    )

    status = step.get(
        "status",
        progress_label(
            step_progress
        ),
    )

    icon = status_icon(
        step_progress
    )

    st.write(
        f"{icon} **{step_id} — {name}**"
    )

    st.progress(
        step_progress / 100,
    )

    metric1, metric2, metric3 = st.columns(
        3
    )

    with metric1:
        st.metric(
            "Progress",
            f"{step_progress}%",
        )

    with metric2:
        st.metric(
            "Weight",
            f"{weight}%",
        )

    with metric3:
        st.metric(
            "Status",
            status,
        )

    with st.expander(
        f"🔎 {step_id} telemetry",
        expanded=False,
    ):

        automatic = step.get(
            "automatic_progress",
            0,
        )

        st.write(
            f"Automatic evidence progress: "
            f"**{automatic}%**"
        )

        st.write(
            f"Engineering weight: "
            f"**{weight}%**"
        )

        st.write(
            f"Current state: "
            f"**{status}**"
        )


# =============================================================================
# MILESTONE MONITOR
# =============================================================================

st.divider()

st.subheader(
    "📊 MILESTONE TELEMETRY"
)

milestones = control.get(
    "milestones",
    {},
)

for step in steps:

    step_id = step.get(
        "id"
    )

    group = milestones.get(
        step_id
    )

    if not group:
        continue

    items = group.get(
        "items",
        [],
    )

    completed_items = sum(
        1
        for item in items
        if item.get(
            "completed",
            False,
        )
    )

    total_items = len(items)

    milestone_progress = (
        completed_items / total_items
        if total_items
        else 0
    )

    with st.expander(
        f"⚔️ {step_id} — "
        f"{completed_items}/{total_items} milestones",
        expanded=False,
    ):

        st.progress(
            milestone_progress
        )

        for item in items:

            if item.get(
                "completed",
                False,
            ):

                st.write(
                    "✅ "
                    + item.get(
                        "name",
                        item.get(
                            "id",
                            "Milestone",
                        ),
                    )
                )

            else:

                st.write(
                    "⬜ "
                    + item.get(
                        "name",
                        item.get(
                            "id",
                            "Milestone",
                        ),
                    )
                )


# =============================================================================
# NEXT STEP
# =============================================================================

st.divider()

st.subheader(
    "🏁 NEXT ENGINEERING STEP"
)

next_step = get_next_step(
    steps
)

if next_step:

    next_id = next_step.get(
        "id",
        "UNKNOWN",
    )

    next_name = next_step.get(
        "name",
        "Unknown",
    )

    next_progress = int(
        next_step.get(
            "progress",
            0,
        )
    )

    st.info(
        f"**{next_id} — {next_name}**\n\n"
        f"Current progress: "
        f"**{next_progress}%**"
    )

else:

    st.success(
        "🏆 All roadmap stages are complete."
    )


# =============================================================================
# GIT TELEMETRY
# =============================================================================

st.divider()

st.subheader(
    "📡 GIT TELEMETRY"
)

git1, git2, git3 = st.columns(3)

with git1:
    st.metric(
        "Branch",
        get_git_branch() or "UNKNOWN",
    )

with git2:
    st.metric(
        "Working Tree",
        get_git_status(),
    )

with git3:

    commit = get_git_value(
        [
            "rev-parse",
            "--short",
            "HEAD",
        ]
    )

    st.metric(
        "HEAD",
        commit or "UNKNOWN",
    )


# =============================================================================
# AUDIT
# =============================================================================

st.divider()

st.subheader(
    "📋 AUDIT LOG"
)

audit = control.get(
    "audit",
    {}
)

events = audit.get(
    "events",
    [],
)

if events:

    recent_events = events[-10:]

    for event in reversed(
        recent_events
    ):

        timestamp = event.get(
            "timestamp",
            "UNKNOWN",
        )

        actor = event.get(
            "actor",
            "UNKNOWN",
        )

        action = event.get(
            "action",
            "UNKNOWN",
        )

        st.write(
            f"**{timestamp}** — "
            f"`{actor}` — "
            f"{action}"
        )

else:

    st.info(
        "No audit events recorded."
    )


# =============================================================================


# =============================================================================
# EINSTEIN AI V2 — OWNER COMMAND CENTER V4
# BLEACH × F1 / RACE CONTROL
# =============================================================================

st.divider()

st.title(
    "🏎️ EINSTEIN AI V2 — OWNER RACE CONTROL"
)

st.caption(
    "⚔️ ZANPAKUTŌ ENGINEERING COMMAND CENTER"
)

# -------------------------------------------------------------------------
# F1 / BLEACH STATUS HEADER
# -------------------------------------------------------------------------

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

control = load_control()

steps = control.get(
    "steps",
    [],
)

overall_progress = calculate_overall_progress(
    control,
    steps,
)

project_data = control.get(
    "project",
    {},
)

current_step_id = project_data.get(
    "current_step",
    "UNKNOWN",
)

with status_col1:
    st.metric(
        "🏁 Overall Progress",
        f"{overall_progress}%",
    )

with status_col2:
    st.metric(
        "⚔️ Roadmap Stages",
        str(len(steps)),
    )

with status_col3:
    completed_stages = sum(
        1
        for step in steps
        if str(
            step.get(
                "status",
                "",
            )
        ).lower()
        in {
            "completed",
            "complete",
        }
        or int(
            step.get(
                "progress",
                0,
            )
        )
        >= 100
    )

    st.metric(
        "🏆 Completed",
        f"{completed_stages}/{len(steps)}",
    )

with status_col4:
    if owner_authorized():
        st.metric(
            "🔐 Access",
            "OWNER",
        )
    else:
        st.metric(
            "👁️ Access",
            "VIEWER",
        )


# -------------------------------------------------------------------------
# MAIN PROGRESS
# -------------------------------------------------------------------------

st.subheader(
    "📊 ENGINEERING TELEMETRY"
)

st.progress(
    max(
        0.0,
        min(
            float(overall_progress) / 100.0,
            1.0,
        ),
    )
)

st.caption(
    f"Weighted engineering progress: {overall_progress}%"
)


# -------------------------------------------------------------------------
# DOMAIN PROGRESS
# -------------------------------------------------------------------------

st.subheader(
    "🧠 SYSTEM PROGRESS"
)

domain_map = {
    "V2-FOUNDATION": "Foundation",
    "V2-DATA": "Knowledge / Data",
    "V2-COG": "Cognitive Architecture",
    "V2-MON": "Monitoring",
    "V2-REASON": "Reasoning Engine",
    "V2-MODEL": "Model Engineering",
    "V2-EVAL": "Evaluation",
    "V2-DEPLOY": "Deployment",
}

domain_cols = st.columns(2)

for index, (step_id, label) in enumerate(
    domain_map.items()
):

    matching_step = next(
        (
            step
            for step in steps
            if step.get("id") == step_id
        ),
        None,
    )

    progress_value = 0

    if matching_step is not None:
        progress_value = int(
            matching_step.get(
                "progress",
                0,
            )
        )

    progress_value = max(
        0,
        min(
            progress_value,
            100,
        ),
    )

    with domain_cols[index % 2]:

        st.write(
            f"**{label}** — {progress_value}%"
        )

        st.progress(
            progress_value / 100.0
        )


# -------------------------------------------------------------------------
# ROADMAP RACE
# -------------------------------------------------------------------------

st.divider()

st.subheader(
    "🏎️ ROADMAP RACE"
)

for index, step in enumerate(steps, start=1):

    step_id = str(
        step.get(
            "id",
            f"STEP-{index}",
        )
    )

    step_name = str(
        step.get(
            "name",
            step.get(
                "title",
                "Unnamed Step",
            ),
        )
    )

    step_progress = int(
        step.get(
            "progress",
            0,
        )
    )

    step_status = str(
        step.get(
            "status",
            "pending",
        )
    )

    weight = int(
        step.get(
            "weight",
            0,
        )
    )

    step_progress = max(
        0,
        min(
            step_progress,
            100,
        ),
    )

    if step_progress >= 100:
        marker = "🏆"

    elif step_progress > 0:
        marker = "🟡"

    else:
        marker = "⬜"

    with st.expander(
        f"{marker} {step_id} — {step_name}",
        expanded=(
            step_id == current_step_id
        ),
    ):

        step_col1, step_col2, step_col3 = (
            st.columns(3)
        )

        with step_col1:
            st.metric(
                "Progress",
                f"{step_progress}%",
            )

        with step_col2:
            st.metric(
                "Weight",
                f"{weight}%",
            )

        with step_col3:
            st.metric(
                "Status",
                step_status.upper(),
            )

        st.progress(
            step_progress / 100.0
        )


# -------------------------------------------------------------------------
# CURRENT MISSION
# -------------------------------------------------------------------------

st.divider()

st.subheader(
    "🎯 CURRENT MISSION"
)

current_step = next(
    (
        step
        for step in steps
        if step.get("id") == current_step_id
    ),
    None,
)

if current_step:

    current_name = current_step.get(
        "name",
        current_step_id,
    )

    current_progress = int(
        current_step.get(
            "progress",
            0,
        )
    )

    st.info(
        f"🏎️ **{current_step_id} — {current_name}**"
    )

    st.progress(
        max(
            0.0,
            min(
                current_progress / 100.0,
                1.0,
            ),
        )
    )

    st.caption(
        f"Current mission progress: {current_progress}%"
    )

else:

    st.info(
        "No active roadmap mission selected."
    )


# -------------------------------------------------------------------------
# OWNER WRITE CONTROL
# -------------------------------------------------------------------------

st.divider()

st.subheader(
    "🔐 OWNER RACE CONTROL"
)

if owner_authorized():

    st.success(
        "🔓 OWNER AUTHORIZATION ACTIVE"
    )

    # -------------------------------------------------------------
    # SELECT ROADMAP STEP
    # -------------------------------------------------------------

    step_options = [
        step.get(
            "id",
            f"STEP-{index}",
        )
        for index, step in enumerate(
            steps,
            start=1,
        )
    ]

    if step_options:

        selected_step_id = st.selectbox(
            "Select engineering step",
            step_options,
        )

        selected_step = next(
            (
                step
                for step in steps
                if step.get("id")
                == selected_step_id
            ),
            None,
        )

        if selected_step:

            selected_name = selected_step.get(
                "name",
                selected_step_id,
            )

            selected_progress = int(
                selected_step.get(
                    "progress",
                    0,
                )
            )

            selected_status = str(
                selected_step.get(
                    "status",
                    "pending",
                )
            )

            st.write(
                f"**{selected_step_id} — "
                f"{selected_name}**"
            )

            new_progress = st.slider(
                "Owner progress override",
                min_value=0,
                max_value=100,
                value=max(
                    0,
                    min(
                        selected_progress,
                        100,
                    ),
                ),
                step=5,
            )

            status_options = [
                "pending",
                "in_progress",
                "completed",
            ]

            if selected_status not in status_options:
                selected_status = "pending"

            new_status = st.selectbox(
                "Engineering status",
                status_options,
                index=status_options.index(
                    selected_status
                ),
            )

            update_col1, update_col2 = st.columns(2)

            with update_col1:

                if st.button(
                    "💾 Save Owner Progress",
                    use_container_width=True,
                ):

                    control = load_control()

                    live_steps = control.get(
                        "steps",
                        [],
                    )

                    target = next(
                        (
                            item
                            for item in live_steps
                            if item.get("id")
                            == selected_step_id
                        ),
                        None,
                    )

                    if target is None:

                        st.error(
                            "Selected roadmap step "
                            "no longer exists."
                        )

                    else:

                        target["progress"] = (
                            new_progress
                        )

                        target["status"] = (
                            new_status
                        )

                        project = control.setdefault(
                            "project",
                            {},
                        )

                        project[
                            "last_updated"
                        ] = datetime.now(
                            timezone.utc
                        ).isoformat()

                        add_audit_event(
                            control,
                            "OWNER_PROGRESS_UPDATED",
                            st.session_state.owner_username,
                        )

                        save_control(
                            control
                        )

                        st.success(
                            "✅ Owner progress saved."
                        )

                        st.toast(
                            "🏎️ Progress telemetry updated!"
                        )

                        st.rerun()

            with update_col2:

                if st.button(
                    "🏁 Approve Current Step",
                    use_container_width=True,
                ):

                    control = load_control()

                    live_steps = control.get(
                        "steps",
                        [],
                    )

                    target = next(
                        (
                            item
                            for item in live_steps
                            if item.get("id")
                            == selected_step_id
                        ),
                        None,
                    )

                    if target is None:

                        st.error(
                            "Selected step not found."
                        )

                    else:

                        target["status"] = (
                            "completed"
                        )

                        target["progress"] = 100

                        project = control.setdefault(
                            "project",
                            {},
                        )

                        project[
                            "last_updated"
                        ] = datetime.now(
                            timezone.utc
                        ).isoformat()

                        add_audit_event(
                            control,
                            "OWNER_STEP_APPROVED",
                            st.session_state.owner_username,
                        )

                        save_control(
                            control
                        )

                        st.success(
                            "🏆 Engineering step approved."
                        )

                        st.toast(
                            "🏆 Step complete — telemetry updated!"
                        )

                        st.rerun()


# -------------------------------------------------------------------------
# NEXT STEP AUTHORIZATION
# -------------------------------------------------------------------------

st.subheader(
    "⏭️ NEXT ENGINEERING STEP"
)

next_step = get_next_step(
    steps
)

if next_step:

    next_id = next_step.get(
        "id",
        "UNKNOWN",
    )

    next_name = next_step.get(
        "name",
        "Unknown",
    )

    next_progress = int(
        next_step.get(
            "progress",
            0,
        )
    )

    st.info(
        f"**{next_id} — {next_name}**"
    )

    st.progress(
        next_progress / 100.0
    )

    if owner_authorized():

        if st.button(
            "▶️ Authorize Next Engineering Step",
            use_container_width=True,
        ):

            control = load_control()

            live_steps = control.get(
                "steps",
                [],
            )

            target_id = next_step.get(
                "id"
            )

            target = next(
                (
                    item
                    for item in live_steps
                    if item.get("id")
                    == target_id
                ),
                None,
            )

            if target is None:

                st.error(
                    "Next step could not be found."
                )

            else:

                control.setdefault(
                    "project",
                    {},
                )[
                    "current_step"
                ] = target_id

                control[
                    "project"
                ][
                    "last_updated"
                ] = datetime.now(
                    timezone.utc
                ).isoformat()

                add_audit_event(
                    control,
                    "OWNER_NEXT_STEP_AUTHORIZED",
                    st.session_state.owner_username,
                )

                save_control(
                    control
                )

                st.success(
                    f"▶️ {target_id} authorized."
                )

                st.toast(
                    "🏎️ Next engineering stage authorized!"
                )

                st.rerun()

    else:

        st.warning(
            "🔒 Owner authorization required."
        )

else:

    st.success(
        "🏆 All roadmap stages are complete."
    )


# -------------------------------------------------------------------------
# AUDIT TELEMETRY
# -------------------------------------------------------------------------

st.divider()

st.subheader(
    "📜 OWNER AUDIT TELEMETRY"
)

latest_control = load_control()

audit = latest_control.get(
    "audit",
    {},
)

events = audit.get(
    "events",
    [],
)

if events:

    for event in reversed(
        events[-10:]
    ):

        timestamp_value = event.get(
            "timestamp",
            "UNKNOWN",
        )

        actor = event.get(
            "actor",
            "UNKNOWN",
        )

        action = event.get(
            "action",
            "UNKNOWN",
        )

        st.write(
            f"**{timestamp_value}**  "
            f"— `{actor}` — `{action}`"
        )

else:

    st.caption(
        "No owner audit events recorded."
    )


# -------------------------------------------------------------------------
# F1 / BLEACH COMMAND STATUS
# -------------------------------------------------------------------------

st.divider()

quote_col1, quote_col2 = st.columns(2)

with quote_col1:

    st.info(
        "🏎️ **MAX VERSTAPPEN MODE**\n\n"
        "Focus. Consistency. Execute. "
        "Improve every lap."
    )

with quote_col2:

    st.warning(
        "⚔️ **ZANPAKUTŌ MODE**\n\n"
        "Every milestone is a battle. "
        "Every validation is a release gate."
    )



# FOOTER
# =============================================================================

st.divider()

st.caption(
    "⚡ Einstein AI V2 • "
    "Owner Command Center • "
    "JSON Source of Truth"
)
