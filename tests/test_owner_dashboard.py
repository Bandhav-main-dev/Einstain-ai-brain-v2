from monitor import owner_dashboard


def test_load_project_state():
    state = owner_dashboard.load_project_state()

    assert isinstance(state, dict)
    assert state.get("project") == "Einstein AI V2"


def test_load_events():
    events = owner_dashboard.load_events()

    assert isinstance(events, list)


def test_recent_events():
    events = [
        {"message": "event 1"},
        {"message": "event 2"},
        {"message": "event 3"},
    ]

    recent = owner_dashboard.get_recent_events(
        events,
        limit=2,
    )

    assert len(recent) == 2
    assert recent[0]["message"] == "event 3"
    assert recent[1]["message"] == "event 2"


def test_progress_value_is_available():
    state = owner_dashboard.load_project_state()

    progress = float(
        state.get(
            "overall_progress",
            state.get("progress_percent", 0.0),
        )
        or 0.0
    )

    assert 0.0 <= progress <= 100.0
