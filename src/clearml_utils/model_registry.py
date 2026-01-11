"""ClearML model registry utilities."""

from typing import Any

from clearml import Model, Task


def register_model(
    model_path: str,
    model_name: str,
    project_name: str = "EPML",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    task: Task | None = None,
) -> Model:
    """Register model in ClearML model registry.

    Args:
        model_path: Path to model file
        model_name: Name of the model
        project_name: Name of the project
        tags: List of tags for the model
        metadata: Dictionary of metadata
        task: ClearML task (if None, uses current task)

    Returns:
        ClearML Model object
    """
    if task is None:
        task = Task.current_task()
        if task is None:
            raise ValueError("No ClearML task found. Call setup_clearml() first.")

    # Create model
    model = Model.create(
        name=model_name,
        project=project_name,
        tags=tags or [],
    )

    # Update model with weights
    model.update_weights(model_path)

    # Add metadata
    if metadata:
        for key, value in metadata.items():
            model.metadata[key] = value

    # Link model to task
    model.update_task(task.id)

    return model


def get_model_versions(
    model_name: str,
    project_name: str = "EPML",
) -> list[Model]:
    """Get all versions of a model.

    Args:
        model_name: Name of the model
        project_name: Name of the project

    Returns:
        List of model versions
    """
    models = Model.list_models(
        project_name=project_name,
        model_name=model_name,
    )
    return list(models) if models else []


def compare_models(
    model_name: str,
    project_name: str = "EPML",
    metric: str = "accuracy",
) -> list[dict[str, Any]]:
    """Compare different versions of a model.

    Args:
        model_name: Name of the model
        project_name: Name of the project
        metric: Metric to compare

    Returns:
        List of model version dictionaries
    """
    models = get_model_versions(model_name, project_name)

    versions = []
    for model in models:
        # Get task associated with model
        task_id = model.task
        if task_id:
            task = Task.get_task(task_id)
            metrics = task.get_last_scalar_metrics()
            metric_value = None
            if metrics:
                for series_name, series_data in metrics.items():
                    if metric in series_name.lower():
                        metric_value = series_data.get("last", {}).get("value")
                        break

            versions.append(
                {
                    "model_id": model.id,
                    "version": model.version,
                    "created": model.created,
                    "metric": metric_value,
                    "metadata": model.metadata,
                    "tags": model.tags,
                }
            )

    # Sort by metric value
    versions.sort(key=lambda x: x["metric"] or 0, reverse=True)

    return versions


def get_best_model(
    model_name: str,
    project_name: str = "EPML",
    metric: str = "accuracy",
) -> Model | None:
    """Get the best model version based on a metric.

    Args:
        model_name: Name of the model
        project_name: Name of the project
        metric: Metric to use for comparison

    Returns:
        Best model or None if no models found
    """
    versions = compare_models(model_name, project_name, metric)
    if not versions:
        return None

    best_version = versions[0]
    models = get_model_versions(model_name, project_name)
    for model in models:
        if model.id == best_version["model_id"]:
            return model

    return None
