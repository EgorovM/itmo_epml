"""Script to create and run ClearML pipelines."""

import logging
import sys
from pathlib import Path

# Add project root to path before imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from clearml import Task  # noqa: E402

from src.clearml_utils.pipeline import create_simple_training_pipeline, run_pipeline  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_existing_tasks():
    """Find existing training tasks that can be used as templates."""
    logger.info("🔍 Looking for existing training tasks...")

    algorithms = ["LogisticRegression", "RandomForest", "KNN"]
    found_tasks = []

    for algorithm in algorithms:
        try:
            # Search for existing tasks
            tasks = Task.query_tasks(
                project_name="EPML",
                task_name=f"{algorithm}_training",
            )

            if tasks:
                # query_tasks returns a list of task IDs (strings)
                task_id = (
                    tasks[0] if isinstance(tasks, list) and len(tasks) > 0 else str(list(tasks)[0])
                )
                found_tasks.append((algorithm, task_id))
                logger.info(f"✅ Found task: {algorithm}_training ({task_id})")
            else:
                logger.warning(f"⚠️ No existing task found for {algorithm}")
        except Exception as e:
            logger.warning(f"⚠️ Could not search for {algorithm}: {e}")

    return found_tasks


def main():
    """Create and run a ClearML pipeline."""
    logger.info("=" * 80)
    logger.info("🚀 ClearML Pipeline Runner")
    logger.info("=" * 80)

    # Find existing tasks to use as templates
    try:
        existing_tasks = find_existing_tasks()
        if not existing_tasks:
            logger.warning("⚠️ No existing tasks found. Please run experiments first:")
            logger.info("   make clearml-experiments")
            return 1
        logger.info(f"✅ Found {len(existing_tasks)} existing tasks")
    except Exception as e:
        logger.warning(f"⚠️ Task search failed: {e}")
        return 1

    # Create pipeline
    try:
        logger.info("🔧 Creating pipeline...")
        pipeline = create_simple_training_pipeline(
            pipeline_name="iris_training_pipeline",
            project_name="EPML",
        )
        logger.info(f"✅ Pipeline created: {pipeline.id}")

        # Pipeline is created but needs to be started manually or via queue
        # For now, we'll just report the pipeline ID
        pipeline_id = pipeline.id if hasattr(pipeline, "id") else None

        logger.info(f"✅ Pipeline created with ID: {pipeline_id}")
        logger.info("📊 View pipeline at: http://localhost:8080/pipelines")
        logger.info("")
        logger.info("ℹ️  Note: To run the pipeline, you need:")
        logger.info("   1. A ClearML agent running on a queue (e.g., 'default' or 'services')")
        logger.info("   2. Or start it manually from the ClearML UI")
        logger.info("")
        logger.info("   To start an agent locally:")
        logger.info("   clearml-agent daemon --queue default")

        # Start pipeline - tasks will be enqueued for agent execution
        try:
            logger.info("")
            logger.info("🔄 Starting pipeline (tasks will be enqueued for agent)...")
            pipeline_id = run_pipeline(
                pipeline,
                queue_name="default",
                wait=False,
            )
            logger.info(f"✅ Pipeline started with ID: {pipeline_id}")
            logger.info("")
            logger.info("📋 Next steps:")
            logger.info("   1. Check that agent is running: ps aux | grep clearml-agent")
            logger.info("   2. Monitor pipeline in UI: http://localhost:8080")
            logger.info("   3. Tasks should change from 'Queued' to 'In Progress' to 'Completed'")
        except Exception as e:
            logger.error(f"❌ Could not start pipeline: {e}")
            logger.info("")
            logger.info("💡 Troubleshooting:")
            logger.info("   1. Make sure agent is running: make clearml-agent-start")
            logger.info("   2. Check agent status in UI: Settings -> Workers")
            logger.info("   3. Or start pipeline manually from ClearML UI")
            return 1

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    logger.info("=" * 80)
    logger.info("✅ Pipeline setup completed!")
    logger.info("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
