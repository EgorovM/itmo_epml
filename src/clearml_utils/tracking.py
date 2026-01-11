"""ClearML experiment tracking utilities."""

from typing import Any

from clearml import OutputModel, Task


def log_parameters(params: dict[str, Any], task: Task | None = None):
    """Log parameters to ClearML.

    Args:
        params: Dictionary of parameters to log
        task: ClearML task (if None, uses current task)
    """
    if task is None:
        task = Task.current_task()
        if task is None:
            raise ValueError("No ClearML task found. Call setup_clearml() first.")

    task.connect(params)


def log_metrics(metrics: dict[str, float], iteration: int = 0, task: Task | None = None):
    """Log metrics to ClearML as scalars.

    Args:
        metrics: Dictionary of metrics to log
        iteration: Iteration number
        task: ClearML task (if None, uses current task)
    """
    if task is None:
        task = Task.current_task()
        if task is None:
            raise ValueError("No ClearML task found. Call setup_clearml() first.")

    # Log as scalars (automatically creates plots in ClearML UI)
    for metric_name, metric_value in metrics.items():
        task.logger.report_scalar(
            title="Metrics",
            series=metric_name,
            value=float(metric_value),
            iteration=iteration,
        )


def log_model(
    model_path: str,
    model_name: str,
    tags: list[str] | None = None,
    task: Task | None = None,
    metadata: dict[str, Any] | None = None,
    model_object: Any = None,
) -> OutputModel:
    """Register model in ClearML.

    Args:
        model_path: Path to model file
        model_name: Name of the model
        tags: List of tags for the model
        task: ClearML task (if None, uses current task)
        metadata: Dictionary of metadata to attach to the model
        model_object: The actual sklearn model object (optional)

    Returns:
        ClearML OutputModel object
    """
    if task is None:
        task = Task.current_task()
        if task is None:
            raise ValueError("No ClearML task found. Call setup_clearml() first.")

    # Combine tags with metadata tags
    all_tags = list(tags or [])
    if metadata:
        for key, value in metadata.items():
            all_tags.append(f"{key}={value}")

    # Create OutputModel with framework specification
    model = OutputModel(task=task, name=model_name, tags=all_tags, framework="scikit-learn")

    # Update weights from file (ClearML automatically tracks the model)
    model.update_weights(model_path)

    # Log model type and parameters as labels if model object provided
    if model_object is not None:
        try:
            model_type = type(model_object).__name__
            task.set_model_label("model_type", model_type)

            if hasattr(model_object, "get_params"):
                params = model_object.get_params()
                for key, value in params.items():
                    task.set_model_label(f"param_{key}", str(value))
        except Exception:
            pass

    # Add metadata as model labels
    if metadata:
        for key, value in metadata.items():
            try:
                task.set_model_label(key, str(value))
            except Exception:
                pass

    return model


def log_artifacts(artifacts: dict[str, str], task: Task | None = None):
    """Log artifacts to ClearML.

    Args:
        artifacts: Dictionary mapping artifact names to file paths
        task: ClearML task (if None, uses current task)
    """
    if task is None:
        task = Task.current_task()
        if task is None:
            raise ValueError("No ClearML task found. Call setup_clearml() first.")

    for artifact_name, artifact_path in artifacts.items():
        task.upload_artifact(name=artifact_name, artifact_object=artifact_path)


def compare_experiments(
    project_name: str = "EPML",
    metric: str = "accuracy",
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Compare experiments in a project.

    Args:
        project_name: Name of the ClearML project
        metric: Metric to compare
        top_n: Number of top experiments to return

    Returns:
        List of experiment dictionaries
    """
    from clearml import Task

    # Get all tasks in the project
    tasks = Task.get_tasks(project_name=project_name)

    experiments = []
    for task in tasks:
        if hasattr(task, "status") and task.status == "completed":
            # Get metrics
            try:
                metrics = task.get_last_scalar_metrics()
                metric_value = None
                if metrics:
                    for series_name, series_data in metrics.items():
                        if metric in series_name.lower():
                            if isinstance(series_data, dict) and "last" in series_data:
                                metric_value = series_data["last"].get("value")
                                break
            except Exception:
                metric_value = None

            # Get parameters
            try:
                params = task.get_parameters()
            except Exception:
                params = {}

            experiments.append(
                {
                    "task_id": getattr(task, "id", "unknown"),
                    "task_name": getattr(task, "name", "unknown"),
                    "status": getattr(task, "status", "unknown"),
                    "metric": metric_value,
                    "parameters": params,
                    "tags": getattr(task, "tags", []),
                }
            )

    # Sort by metric value
    experiments.sort(key=lambda x: x["metric"] or 0, reverse=True)

    return experiments[:top_n]
