from monitor.schema import (
    ProjectEvent,
    ProjectState,
    event_to_json,
    state_to_json,
    validate_project_event,
    validate_project_state,
)


def test_project_state_schema():
    state = ProjectState(
        current_phase="0.6.2",
        current_step="Monitoring Schema",
        status="RUNNING",
        progress_percent=12.5,
        active_branch="feature/monitoring-system",
        current_commit="abc123",
    )

    errors = validate_project_state(state)

    assert errors == []
    assert state.project == "Einstein AI V2"
    assert state.status == "RUNNING"
    assert state.progress_percent == 12.5


def test_project_state_rejects_invalid_progress():
    state = ProjectState(progress_percent=101)

    errors = validate_project_state(state)

    assert "progress_percent must be between 0 and 100" in errors


def test_project_event_schema():
    event = ProjectEvent(
        event_id="evt-001",
        timestamp="2026-08-28T00:00:00+00:00",
        phase="0.6.2",
        step="Monitoring Schema",
        event_type="STEP_STARTED",
        level="INFO",
        message="Phase 0.6.2 started.",
        status="RUNNING",
        progress_percent=10.0,
    )

    errors = validate_project_event(event)

    assert errors == []
    assert event.event_type == "STEP_STARTED"


def test_project_event_rejects_missing_message():
    event = ProjectEvent(
        event_id="evt-002",
        timestamp="2026-08-28T00:00:00+00:00",
        phase="0.6.2",
        step="Monitoring Schema",
        event_type="TEST",
        level="INFO",
        message="",
    )

    errors = validate_project_event(event)

    assert "message is required" in errors


def test_json_serialization():
    state = ProjectState(
        current_phase="0.6.2",
        current_step="Monitoring Schema",
        progress_percent=25.0,
    )

    event = ProjectEvent(
        event_id="evt-003",
        timestamp="2026-08-28T00:00:00+00:00",
        phase="0.6.2",
        step="Monitoring Schema",
        event_type="TEST",
        level="INFO",
        message="Serialization test",
    )

    state_json = state_to_json(state)
    event_json = event_to_json(event)

    assert '"Einstein AI V2"' in state_json
    assert '"Serialization test"' in event_json
