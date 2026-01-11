"""Create properly configured tasks for pipeline execution."""

import logging
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from clearml import Task  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_pipeline_task(algorithm_name: str, params: dict[str, Any]):
    """Create a task configured for pipeline execution.

    Args:
        algorithm_name: Name of the algorithm
        params: Parameters for the algorithm
    """
    project_root = Path.cwd()

    # Create task
    from clearml import Task as ClearMLTask

    task: ClearMLTask = Task.init(
        project_name="EPML",
        task_name=f"{algorithm_name}_pipeline_task",
        tags=[algorithm_name, "pipeline", "template"],
    )

    # Configure script for agent execution
    # The script should be executable by agent
    task.set_script(
        repository="",  # Local execution, no git clone
        entry_point="src/clearml_utils/train_with_clearml.py",
        working_dir=str(project_root),
    )

    # Set parameters that will be used by the script
    # Note: train_with_clearml.py needs to be modified to accept these parameters
    task.connect(
        {
            "algorithm_name": algorithm_name,
            "params": params,
        }
    )

    # Set requirements file so agent installs dependencies
    # Note: ClearML Task doesn't have set_requirements method directly
    # Requirements are typically handled via pip packages or docker image
    # The agent will use the requirements.txt from the working directory

    # Close task (it will be used as template)
    task.close()

    logger.info(f"✅ Created pipeline task: {task.id} for {algorithm_name}")
    return task.id


def main():
    """Create all pipeline tasks."""
    algorithms: dict[str, dict[str, Any]] = {
        "LogisticRegression": {
            "max_iter": 1000,
            "solver": "lbfgs",
            "algorithm": "LogisticRegression",
        },
        "RandomForest": {
            "n_estimators": 100,
            "max_depth": None,
            "algorithm": "RandomForest",
        },
        "KNN": {
            "n_neighbors": 5,
            "algorithm": "KNN",
        },
    }

    logger.info("Creating pipeline tasks...")
    for algorithm, params in algorithms.items():
        try:
            create_pipeline_task(algorithm, params)
        except Exception as e:
            logger.error(f"Failed to create task for {algorithm}: {e}")

    logger.info("✅ All pipeline tasks created!")


if __name__ == "__main__":
    main()
