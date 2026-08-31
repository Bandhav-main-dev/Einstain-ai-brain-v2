import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTROL_FILE = PROJECT_ROOT / "project_control.json"


def load_control() -> dict:
    """Load project control JSON."""

    with CONTROL_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_control(control: dict) -> None:
    """Save project control JSON."""

    control.setdefault(
        "project",
        {},
    )

    control["project"]["last_updated"] = (
        datetime.now(timezone.utc).isoformat()
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


def resolve_path(path: str) -> Path:
    """Resolve a project-relative path safely."""

    candidate = (
        PROJECT_ROOT / path
    ).resolve()

    project_root = PROJECT_ROOT.resolve()

    if candidate != project_root and project_root not in candidate.parents:
        raise ValueError(
            f"Unsafe project path: {path}"
        )

    return candidate


def file_exists(path: str) -> bool:
    """Check whether a file exists."""

    return resolve_path(path).is_file()


def directory_exists(path: str) -> bool:
    """Check whether a directory exists."""

    return resolve_path(path).is_dir()


def file_any(paths: list[str]) -> bool:
    """Check whether any listed file exists."""

    return any(
        file_exists(path)
        for path in paths
    )


def directory_any(paths: list[str]) -> bool:
    """Check whether any listed directory exists."""

    return any(
        directory_exists(path)
        for path in paths
    )


def json_key(control: dict, path: str) -> bool:
    """Check whether a nested JSON key exists."""

    current = control

    for part in path.split("."):

        if not isinstance(current, dict):
            return False

        if part not in current:
            return False

        current = current[part]

    return True


def progress_key(control: dict, path: str) -> bool:
    """Check whether a progress value exists."""

    current = control

    for part in path.split("."):

        if not isinstance(current, dict):
            return False

        if part not in current:
            return False

        current = current[part]

    try:
        value = float(current)
    except (TypeError, ValueError):
        return False

    return 0 <= value <= 100


def python_compile(path: str) -> bool:
    """Compile a Python file."""

    target = resolve_path(path)

    if not target.is_file():
        return False

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(target),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def check_milestone(
    control: dict,
    milestone: dict,
) -> bool:
    """Evaluate one milestone."""

    milestone_type = milestone.get(
        "type"
    )

    if milestone_type == "file_exists":
        return file_exists(
            milestone["path"]
        )

    if milestone_type == "directory_exists":
        return directory_exists(
            milestone["path"]
        )

    if milestone_type == "file_any":
        return file_any(
            milestone["paths"]
        )

    if milestone_type == "directory_any":
        return directory_any(
            milestone["paths"]
        )

    if milestone_type == "json_key":
        return json_key(
            control,
            milestone["path"],
        )

    if milestone_type == "progress_key":
        return progress_key(
            control,
            milestone["path"],
        )

    if milestone_type == "python_compile":
        return python_compile(
            milestone["path"]
        )

    return False


def calculate_step_progress(
    milestone_group: dict,
) -> int:
    """Calculate weighted milestone progress."""

    items = milestone_group.get(
        "items",
        [],
    )

    total_weight = 0.0
    completed_weight = 0.0

    for item in items:

        weight = float(
            item.get(
                "weight",
                1,
            )
        )

        total_weight += weight

        if item.get(
            "completed",
            False,
        ):
            completed_weight += weight

    if total_weight <= 0:
        return 0

    return round(
        (
            completed_weight
            / total_weight
        )
        * 100
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

        weight = float(
            step.get(
                "weight",
                1,
            )
        )

        progress = float(
            step.get(
                "progress",
                0,
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


def run_monitoring(
    control: dict | None = None,
) -> dict:
    """Run all automatic milestone checks."""

    if control is None:
        control = load_control()

    milestone_groups = control.get(
        "milestones",
        {},
    )

    steps = control.get(
        "steps",
        [],
    )

    results = []

    for step in steps:

        step_id = step.get(
            "id"
        )

        group = milestone_groups.get(
            step_id
        )

        if not group:
            continue

        for item in group.get(
            "items",
            [],
        ):

            completed = check_milestone(
                control,
                item,
            )

            item["completed"] = completed

            item["checked_at"] = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

            results.append(
                {
                    "step": step_id,
                    "milestone": item.get(
                        "id"
                    ),
                    "completed": completed,
                }
            )

        calculated_progress = (
            calculate_step_progress(
                group
            )
        )

        # IMPORTANT:
        # Only replace the step progress when
        # automatic milestone evidence is available.
        #
        # This prevents unknown future work from
        # being falsely marked complete.

        step["automatic_progress"] = (
            calculated_progress
        )

        if calculated_progress > 0:

            step["progress"] = max(
                int(
                    step.get(
                        "progress",
                        0,
                    )
                ),
                calculated_progress,
            )

        if step.get(
            "progress",
            0,
        ) >= 100:

            step["status"] = "completed"

        elif step.get(
            "progress",
            0,
        ) > 0:

            step["status"] = "in_progress"

        else:

            step["status"] = "pending"

    overall = calculate_overall_progress(
        control
    )

    control.setdefault(
        "progress",
        {},
    )

    control["progress"]["overall"] = (
        overall
    )

    control["progress"]["calculation"] = {
        "method": "weighted_roadmap",
        "automatic_milestones": True,
    }

    control.setdefault(
        "monitoring",
        {},
    )

    control["monitoring"]["last_run"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    control["monitoring"]["milestones_checked"] = (
        len(results)
    )

    control["monitoring"]["milestones_completed"] = (
        sum(
            1
            for result in results
            if result["completed"]
        )
    )

    control["monitoring"]["status"] = (
        "healthy"
    )

    control.setdefault(
        "audit",
        {},
    )

    events = control["audit"].setdefault(
        "events",
        [],
    )

    events.append(
        {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "actor": "monitoring_engine",
            "action": "automatic_progress_scan",
            "overall_progress": overall,
            "milestones_checked": len(
                results
            ),
            "milestones_completed": sum(
                1
                for result in results
                if result["completed"]
            ),
        }
    )

    control["audit"]["last_action"] = (
        "Automatic milestone progress scan"
    )

    control["audit"]["last_actor"] = (
        "monitoring_engine"
    )

    save_control(
        control
    )

    return {
        "overall_progress": overall,
        "results": results,
    }


if __name__ == "__main__":

    result = run_monitoring()

    print("=" * 80)
    print("EINSTEIN AI V2 — AUTOMATIC PROGRESS SCAN")
    print("=" * 80)

    print(
        f"Overall progress: "
        f"{result['overall_progress']}%"
    )

    print(
        f"Milestones checked: "
        f"{len(result['results'])}"
    )

    print(
        f"Milestones completed: "
        f"{sum(1 for item in result['results'] if item['completed'])}"
    )

    print("\nMILESTONES")

    for item in result["results"]:

        status = (
            "✅"
            if item["completed"]
            else "⬜"
        )

        print(
            f"{status} "
            f"{item['step']} / "
            f"{item['milestone']}"
        )

    print("=" * 80)
