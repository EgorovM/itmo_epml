"""Setup ClearML configuration."""

import os
from pathlib import Path

from clearml import Task


def setup_clearml(
    project_name: str = "EPML",
    task_name: str | None = None,
    tags: list[str] | None = None,
) -> Task:
    """Setup ClearML task.

    Args:
        project_name: Name of the ClearML project
        task_name: Name of the task (experiment)
        tags: List of tags for the task

    Returns:
        ClearML Task object
    """
    # Initialize ClearML task
    task = Task.init(
        project_name=project_name,
        task_name=task_name,
        tags=tags or [],
    )

    return task


def setup_clearml_offline():
    """Setup ClearML in offline mode for local development."""
    os.environ["CLEARML_OFFLINE_MODE"] = "1"
    os.environ["CLEARML_OUTPUT_URI"] = str(Path("clearml_outputs").absolute())


def get_clearml_config() -> dict:
    """Get ClearML configuration.

    Returns:
        Dictionary with ClearML configuration
    """
    config = {
        "api_server": os.getenv("CLEARML_API_SERVER", "http://localhost:8008"),
        "web_server": os.getenv("CLEARML_WEB_SERVER", "http://localhost:8080"),
        "files_server": os.getenv("CLEARML_FILES_SERVER", "http://localhost:8081"),
        "offline_mode": os.getenv("CLEARML_OFFLINE_MODE", "0") == "1",
    }
    return config
