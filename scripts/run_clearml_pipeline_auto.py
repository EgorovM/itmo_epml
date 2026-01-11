"""Script to automatically create, run, and monitor ClearML pipelines."""

import logging
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from clearml import Task  # noqa: E402

from src.clearml_utils.pipeline import create_simple_training_pipeline, run_pipeline  # noqa: E402
from src.clearml_utils.pipeline_monitor import (  # noqa: E402
    ClearMLPipelineMonitor,
    send_notification,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_existing_tasks():
    """Find existing training tasks that can be used as templates."""
    algorithms = ["LogisticRegression", "RandomForest", "KNN"]
    found_tasks = []

    for algorithm in algorithms:
        try:
            tasks = Task.query_tasks(
                project_name="EPML",
                task_name=f"{algorithm}_training",
            )

            if tasks:
                task_id = (
                    tasks[0] if isinstance(tasks, list) and len(tasks) > 0 else str(list(tasks)[0])
                )
                found_tasks.append((algorithm, task_id))
                logger.info(f"✅ Found task: {algorithm}_training ({task_id})")
        except Exception as e:
            logger.warning(f"⚠️ Could not search for {algorithm}: {e}")

    return found_tasks


def auto_run_pipeline(
    pipeline_name: str = "iris_training_pipeline_auto",
    project_name: str = "EPML",
    queue_name: str = "default",
    monitor: bool = True,
    wait_for_completion: bool = False,
) -> dict[str, Any]:
    """Automatically create, run, and monitor a ClearML pipeline.

    Args:
        pipeline_name: Name of the pipeline
        project_name: Name of the project
        queue_name: Queue name for execution
        monitor: Whether to monitor pipeline execution
        wait_for_completion: Whether to wait for pipeline completion

    Returns:
        Dictionary with pipeline execution results
    """
    logger.info("=" * 80)
    logger.info("🚀 ClearML Pipeline Auto Runner")
    logger.info("=" * 80)

    # Find existing tasks
    try:
        existing_tasks = find_existing_tasks()
        if not existing_tasks:
            logger.warning("⚠️ No existing tasks found. Please run experiments first:")
            logger.info("   make clearml-experiments")
            return {"status": "error", "message": "No existing tasks found"}

        logger.info(f"✅ Found {len(existing_tasks)} existing tasks")
    except Exception as e:
        logger.error(f"❌ Task search failed: {e}")
        return {"status": "error", "error": str(e)}

    # Create pipeline
    try:
        logger.info("🔧 Creating pipeline...")
        pipeline = create_simple_training_pipeline(
            pipeline_name=pipeline_name,
            project_name=project_name,
        )
        pipeline_id = pipeline.id if hasattr(pipeline, "id") else None
        logger.info(f"✅ Pipeline created: {pipeline_id}")

        # Try to start pipeline
        started = False
        try:
            logger.info(f"🚀 Starting pipeline on queue '{queue_name}'...")
            started_pipeline_id = run_pipeline(
                pipeline,
                queue_name=queue_name,
                wait=False,
            )
            if started_pipeline_id:
                pipeline_id = started_pipeline_id
                started = True
                logger.info(f"✅ Pipeline started: {pipeline_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not start pipeline automatically: {e}")
            logger.info(
                "   Pipeline created but not started. Start it manually from UI or with agent."
            )

        # Monitor pipeline if requested (using ClearML API)
        monitor_result = None
        if monitor and started:
            logger.info("🔍 Starting pipeline monitoring via ClearML API...")
            monitor_obj = ClearMLPipelineMonitor()
            if wait_for_completion:
                monitor_result = monitor_obj.monitor_pipeline(
                    pipeline_id,
                    check_interval=10,
                    timeout=3600,  # 1 hour timeout
                )
            else:
                # Just get current status from ClearML
                monitor_result = monitor_obj.get_pipeline_summary(pipeline_id)
                logger.info(f"📊 Current status: {monitor_result.get('status', 'unknown')}")

        # Send notification to ClearML
        if monitor_result:
            status = monitor_result.get("status", "unknown")
            send_notification(pipeline_id, status, monitor_result)
        elif started:
            # Even if not monitoring, send initial notification
            initial_status = {"status": "started", "id": pipeline_id}
            send_notification(pipeline_id, "started", initial_status)

        result = {
            "status": "success" if started else "created",
            "pipeline_id": pipeline_id,
            "started": started,
            "monitor_result": monitor_result,
        }

        logger.info("=" * 80)
        logger.info("✅ Pipeline auto-run completed!")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automatically run ClearML pipeline")
    parser.add_argument(
        "--pipeline-name",
        default="iris_training_pipeline_auto",
        help="Name of the pipeline",
    )
    parser.add_argument(
        "--queue",
        default="default",
        help="Queue name for execution",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        default=True,
        help="Monitor pipeline execution",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for pipeline completion",
    )

    args = parser.parse_args()

    result = auto_run_pipeline(
        pipeline_name=args.pipeline_name,
        queue_name=args.queue,
        monitor=args.monitor,
        wait_for_completion=args.wait,
    )

    return 0 if result.get("status") == "success" or result.get("status") == "created" else 1


if __name__ == "__main__":
    sys.exit(main())
