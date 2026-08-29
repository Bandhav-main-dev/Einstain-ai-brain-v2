from monitor import professor_dashboard


def test_project_state_loader():
    state = professor_dashboard.load_project_state()

    assert isinstance(state, dict)


def test_events_loader():
    events = professor_dashboard.load_events()

    assert isinstance(events, list)
