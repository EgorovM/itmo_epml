"""Setup ClearML configuration."""


from clearml import Task


def setup_clearml(
    project_name: str = "EPML",
    task_name: str | None = None,
    tags: list[str] | None = None,
    reuse_last_task_id: bool = False,
) -> Task:
    """Setup ClearML task.

    Args:
        project_name: Name of the ClearML project
        task_name: Name of the task (experiment)
        tags: List of tags for the task
        reuse_last_task_id: Whether to reuse the last task ID (default: False)

    Returns:
        ClearML Task object
    """
    # Close any existing task first to prevent reuse
    current_task = Task.current_task()
    if current_task is not None:
        try:
            # Only close if it's still running
            status = getattr(current_task, "status", None)
            if status == "running":
                current_task.close()
        except Exception:
            pass

    # Initialize ClearML task (will create new task, not reuse)
    # Disable auto-connecting to prevent git repository detection
    task = Task.init(
        project_name=project_name,
        task_name=task_name,
        tags=tags or [],
        reuse_last_task_id=reuse_last_task_id,
        auto_connect_frameworks=False,
        auto_connect_streams=False,
        auto_connect_arg_parser=False,
    )

    # Clear repository info to prevent agent from trying to clone
    # This allows agent to use local files instead
    try:
        if hasattr(task, "data") and hasattr(task.data, "script"):
            task.data.script.repository = ""
            task.data.script.branch = ""
            task.data.script.commit = ""
            task.data.script.tag = ""
    except Exception:
        pass

    return task
