from monitor.logging_core import log_event, read_events
from monitor.project_state import load_state, save_state


def test_project_state_exists():
    state = load_state()

    assert state["project"] == "Einstein AI V2"
    assert "current_phase" in state
    assert "current_step" in state
    assert "overall_progress" in state


def test_logging_core(tmp_path, monkeypatch):
    from monitor import logging_core

    log_file = tmp_path / "events.jsonl"

    monkeypatch.setattr(
        logging_core,
        "EVENT_LOG",
        log_file,
    )

    monkeypatch.setattr(
        logging_core,
        "LOG_DIR",
        tmp_path,
    )

    event = log_event(
        "test",
        "Monitoring test event.",
        phase="test",
        step="test",
        status="PASS",
    )

    assert event["event_type"] == "test"

    events = read_events()

    assert len(events) == 1
    assert events[0]["status"] == "PASS"


def test_state_round_trip(tmp_path, monkeypatch):
    from monitor import project_state

    state_file = tmp_path / "state.json"

    monkeypatch.setattr(
        project_state,
        "STATE_FILE",
        state_file,
    )

    monkeypatch.setattr(
        project_state,
        "LOG_DIR",
        tmp_path,
    )

    state = {
        "project": "Einstein AI V2",
        "current_phase": "0.6.1",
        "current_step": "test",
        "overall_progress": 25,
    }

    save_state(state)

    loaded = load_state()

    assert loaded["project"] == "Einstein AI V2"
    assert loaded["current_step"] == "test"
    assert loaded["overall_progress"] == 25
