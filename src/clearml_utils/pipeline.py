"""ClearML pipeline utilities."""

import logging
from typing import Any

from clearml import PipelineController, Task

logger = logging.getLogger(__name__)


def create_training_pipeline(
    pipeline_name: str = "iris_training_pipeline",
    project_name: str = "EPML",
    algorithms: list[str] | None = None,
) -> PipelineController:
    """Create a ClearML pipeline for training multiple models.

    Args:
        pipeline_name: Name of the pipeline
        project_name: Name of the project
        algorithms: List of algorithm names to train (if None, uses default set)

    Returns:
        PipelineController object
    """
    if algorithms is None:
        algorithms = ["LogisticRegression", "RandomForest", "KNN"]

    # Create pipeline
    pipeline = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0.0",
    )

    # Add data preparation step (if exists)
    try:
        # Try to find existing prepare_data task
        tasks = Task.query_tasks(project_name=project_name, task_name="prepare_data")
        if tasks:
            pipeline.add_step(
                name="prepare_data",
                base_task_project=project_name,
                base_task_name="prepare_data",
            )
            logger.info("✅ Added prepare_data step")
    except Exception:
        logger.warning("⚠️ prepare_data task not found, skipping")

    # Add training steps for each algorithm
    parent_step = "prepare_data" if "prepare_data" in [s.name for s in pipeline.steps] else None
    for algorithm in algorithms:
        step_name = f"train_{algorithm.lower()}"
        parents = [parent_step] if parent_step else []

        # Try to find existing training task
        try:
            tasks = Task.query_tasks(
                project_name=project_name,
                task_name=f"{algorithm}_training",
            )
            if tasks:
                pipeline.add_step(
                    name=step_name,
                    base_task_project=project_name,
                    base_task_name=f"{algorithm}_training",
                    parents=parents,
                )
                logger.info(f"✅ Added {step_name} step")
                parent_step = step_name  # Chain models sequentially
        except Exception as e:
            logger.warning(f"⚠️ Could not add {step_name}: {e}")

    return pipeline


def run_pipeline(
    pipeline: PipelineController,
    queue_name: str = "default",
    wait: bool = False,
) -> str:
    """Run a ClearML pipeline.

    Args:
        pipeline: PipelineController object
        queue_name: Name of the queue to run on (use 'services' for local execution)
        wait: Whether to wait for pipeline completion

    Returns:
        Pipeline task ID
    """
    pipeline_name = (
        getattr(pipeline._task, "name", "pipeline") if hasattr(pipeline, "_task") else "pipeline"
    )
    logger.info(f"🚀 Starting pipeline '{pipeline_name}' on queue '{queue_name}'...")

    # Start pipeline - this will enqueue all steps to the specified queue
    # The agent will pick up and execute tasks from the queue
    try:
        logger.info(f"🚀 Starting pipeline on queue '{queue_name}'...")
        logger.info(f"   Agent should pick up tasks from queue '{queue_name}'")

        # Start pipeline - this enqueues all steps
        pipeline.start(queue=queue_name)
        pipeline_id = pipeline.id
        project_name = getattr(pipeline, "project", "EPML")

        logger.info(f"✅ Pipeline started: {pipeline_id}")
        logger.info(
            f"📊 View at: http://localhost:8080/projects/{project_name}/experiments/{pipeline_id}"
        )
        logger.info(f"📋 All pipeline steps are enqueued to queue '{queue_name}'")
        logger.info("⏳ Agent will execute tasks automatically...")

        if wait:
            logger.info("⏳ Waiting for pipeline to complete...")
            pipeline.wait()
            logger.info("✅ Pipeline completed!")

        return str(pipeline_id) if pipeline_id is not None else ""
    except Exception as e:
        logger.error(f"❌ Failed to start pipeline: {e}")
        logger.error(f"   Make sure agent is running: clearml-agent daemon --queue {queue_name}")
        raise


def monitor_pipeline(pipeline_id: str) -> dict[str, Any]:
    """Monitor pipeline execution.

    Args:
        pipeline_id: ID of the pipeline task

    Returns:
        Dictionary with pipeline status
    """
    try:
        task = Task.get_task(task_id=pipeline_id)

        status = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "created": str(task.created) if hasattr(task, "created") else None,
            "started": str(task.started) if hasattr(task, "started") else None,
            "completed": str(task.completed) if hasattr(task, "completed") else None,
            "project": getattr(task, "project", "EPML"),
        }

        # Calculate duration if possible
        if hasattr(task, "started") and hasattr(task, "completed"):
            if task.started and task.completed:
                duration = (task.completed - task.started).total_seconds()
                status["duration"] = duration

        return status
    except Exception as e:
        logger.error(f"❌ Failed to get pipeline status: {e}")
        return {"error": str(e)}


def create_simple_training_pipeline(
    pipeline_name: str = "iris_simple_pipeline",
    project_name: str = "EPML",
    algorithms: list[str] | None = None,
) -> PipelineController:
    """Create a simple pipeline that chains training tasks.

    This creates a pipeline that will run training tasks sequentially.
    Uses existing tasks as templates.

    Args:
        pipeline_name: Name of the pipeline
        project_name: Name of the project
        algorithms: List of algorithm names (default: ["LogisticRegression", "RandomForest", "KNN"])

    Returns:
        PipelineController object
    """
    if algorithms is None:
        algorithms = ["LogisticRegression", "RandomForest", "KNN"]

    # Close any existing task first
    current_task = Task.current_task()
    if current_task is not None:
        try:
            current_task.close()
        except Exception:
            pass

    # Create pipeline
    # PipelineController automatically creates a task, which we'll use
    try:
        pipeline = PipelineController(
            name=pipeline_name,
            project=project_name,
            version="1.0.0",
        )
        # Ensure the pipeline task is in the right state
        if hasattr(pipeline, "_task") and pipeline._task:
            # Make sure task is not stopped - mark as started if needed
            try:
                status = getattr(pipeline._task, "status", None)
                if status == "stopped" or status == "closed":
                    # Reopen the task
                    pipeline._task.mark_started(force=True)
            except Exception as e:
                logger.warning(f"Could not update pipeline task status: {e}")
    except Exception as e:
        logger.error(f"Failed to create pipeline: {e}")
        raise

    # Add steps that will use existing tasks as templates
    for i, algorithm in enumerate(algorithms):
        step_name = f"train_{algorithm.lower()}"
        parents = [f"train_{algorithms[i-1].lower()}"] if i > 0 else []

        try:
            pipeline.add_step(
                name=step_name,
                base_task_project=project_name,
                base_task_name=f"{algorithm}_training",
                parents=parents,
                execution_queue="default",  # Set default queue for execution
            )
            logger.info(f"✅ Added {step_name} step")
        except Exception as e:
            logger.warning(f"⚠️ Could not add {step_name}: {e}")

    return pipeline
