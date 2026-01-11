"""ClearML pipeline utilities."""

from typing import Any

from clearml import PipelineController, Task


def create_training_pipeline(
    pipeline_name: str = "iris_training_pipeline",
    project_name: str = "EPML",
) -> PipelineController:
    """Create a ClearML pipeline for training.

    Args:
        pipeline_name: Name of the pipeline
        project_name: Name of the project

    Returns:
        PipelineController object
    """
    # Create pipeline
    pipeline = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0.0",
    )

    # Add steps
    pipeline.add_step(
        name="prepare_data",
        base_task_project=project_name,
        base_task_name="prepare_data",
    )

    pipeline.add_step(
        name="train_model",
        base_task_project=project_name,
        base_task_name="train_model",
        parents=["prepare_data"],
    )

    pipeline.add_step(
        name="evaluate_model",
        base_task_project=project_name,
        base_task_name="evaluate_model",
        parents=["train_model"],
    )

    return pipeline


def run_pipeline(
    pipeline: PipelineController,
    queue_name: str = "default",
) -> str:
    """Run a ClearML pipeline.

    Args:
        pipeline: PipelineController object
        queue_name: Name of the queue to run on

    Returns:
        Pipeline task ID
    """
    # Start pipeline
    pipeline.start(queue=queue_name)

    pipeline_id = pipeline.id
    return str(pipeline_id) if pipeline_id is not None else ""


def monitor_pipeline(pipeline_id: str) -> dict[str, Any]:
    """Monitor pipeline execution.

    Args:
        pipeline_id: ID of the pipeline task

    Returns:
        Dictionary with pipeline status
    """
    task = Task.get_task(task_id=pipeline_id)

    status = {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "created": task.created,
        "started": task.started,
        "completed": task.completed,
    }

    return status
