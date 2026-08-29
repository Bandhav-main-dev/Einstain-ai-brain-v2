from monitor.progress import (
    calculate_overall_progress,
    calculate_step_progress,
)


def test_empty_project_progress():
    progress = calculate_overall_progress(
        [],
        [],
        total_steps=10,
    )

    assert progress == 0.0


def test_active_step_progress():
    progress = calculate_overall_progress(
        [],
        ["0.6.3"],
        total_steps=10,
    )

    assert progress == 5.0


def test_completed_step_progress():
    progress = calculate_overall_progress(
        ["0.6.1"],
        [],
        total_steps=10,
    )

    assert progress == 10.0


def test_step_progress_values():
    assert calculate_step_progress() == 0.0
    assert calculate_step_progress(active=True) == 50.0
    assert calculate_step_progress(completed=True) == 100.0


def test_explicit_step_progress():
    assert (
        calculate_step_progress(
            progress_percent=75,
        )
        == 75.0
    )


def test_progress_is_clamped():
    assert (
        calculate_step_progress(
            progress_percent=150,
        )
        == 100.0
    )

    assert (
        calculate_step_progress(
            progress_percent=-10,
        )
        == 0.0
    )
