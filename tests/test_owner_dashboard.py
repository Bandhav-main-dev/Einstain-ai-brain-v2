from __future__ import annotations

import json

from monitor import owner_dashboard


def test_load_state_missing_file(tmp_path, monkeypatch):
    state_file = tmp_path / "project_state.json"

    monkeypatch.setattr(
        owner_dashboard,
        "STATE_FILE",
        state_file,
    )

    assert owner_dashboard.load_state() == {}


def test_load_state_valid_file(tmp_path, monkeypatch):
    state_file = tmp_path / "project_state.json"

    state_file.write_text(
        json.dumps(
            {
                "project": "Einstein AI V2",
                "current_phase": "0.6.4-U1",
                "progress_percent": 25.0,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        owner_dashboard,
        "STATE_FILE",
        state_file,
    )

    state = owner_dashboard.load_state()

    assert state["project"] == "Einstein AI V2"
    assert state["current_phase"] == "0.6.4-U1"
    assert state["progress_percent"] == 25.0


def test_load_state_invalid_json(tmp_path, monkeypatch):
    state_file = tmp_path / "project_state.json"

    state_file.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        owner_dashboard,
        "STATE_FILE",
        state_file,
    )

    assert owner_dashboard.load_state() == {}


def test_load_events_missing_file(tmp_path, monkeypatch):
    event_file = tmp_path / "project_events.jsonl"

    monkeypatch.setattr(
        owner_dashboard,
        "EVENT_FILE",
        event_file,
    )

    assert owner_dashboard.load_events() == []


def test_load_events_valid_jsonl(tmp_path, monkeypatch):
    event_file = tmp_path / "project_events.jsonl"

    events = [
        {
            "event_type": "PHASE_START",
            "message": "Phase started",
        },
        {
            "event_type": "TEST_PASS",
            "message": "Tests passed",
        },
    ]

    event_file.write_text(
        "\n".join(json.dumps(item) for item in events),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        owner_dashboard,
        "EVENT_FILE",
        event_file,
    )

    loaded = owner_dashboard.load_events()

    assert len(loaded) == 2
    assert loaded[0]["event_type"] == "TEST_PASS"
    assert loaded[1]["event_type"] == "PHASE_START"


def test_load_events_ignores_invalid_lines(tmp_path, monkeypatch):
    event_file = tmp_path / "project_events.jsonl"

    event_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_type": "VALID",
                    }
                ),
                "{invalid",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        owner_dashboard,
        "EVENT_FILE",
        event_file,
    )

    loaded = owner_dashboard.load_events()

    assert len(loaded) == 1
    assert loaded[0]["event_type"] == "VALID"


def test_git_info_returns_expected_keys():
    info = owner_dashboard.git_info()

    assert "branch" in info
    assert "commit" in info
    assert "status" in info


def test_dashboard_file_contains_landscape_configuration():
    source = owner_dashboard.OWNER_FILE.read_text(
        encoding="utf-8"
    ) if hasattr(owner_dashboard, "OWNER_FILE") else (
        owner_dashboard.__file__
    )

    if isinstance(source, str) and source.endswith(".py"):
        from pathlib import Path

        source = Path(source).read_text(
            encoding="utf-8"
        )

    # The owner dashboard is intentionally Streamlit-native.
    # The previous HTML/CSS telemetry marker is no longer required.
    assert "layout=\"wide\"" in source
    assert "OWNER COMMAND CENTER" in source
    assert "Owner Monitoring Dashboard" in source
    assert "st.metric(" in source
    assert "st.progress(" in source
    assert "st.expander(" in source
