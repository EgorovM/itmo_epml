"""Utilities for MLflow experiment tracking."""

from contextlib import contextmanager
from typing import Any

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient


def setup_mlflow(
    tracking_uri: str = "sqlite:///mlflow.db",
    experiment_name: str = "iris-classification",
    reset_db: bool = False,
) -> None:
    """Setup MLflow tracking.

    Args:
        tracking_uri: URI for MLflow tracking (default: SQLite database)
        experiment_name: Name of the experiment
        reset_db: Whether to reset database if there are migration errors
    """
    mlflow.set_tracking_uri(tracking_uri)

    # Reset database if requested or if there's a migration error
    if reset_db and tracking_uri.startswith("sqlite:///"):
        db_path = tracking_uri.replace("sqlite:///", "")
        if db_path:
            import os

            if os.path.exists(db_path):
                os.remove(db_path)
                if os.path.exists(db_path + "-journal"):
                    os.remove(db_path + "-journal")

    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            mlflow.create_experiment(experiment_name)
    except Exception as e:
        # If there's a migration error, try to reset database
        if "revision" in str(e).lower() or "migration" in str(e).lower():
            if tracking_uri.startswith("sqlite:///"):
                db_path = tracking_uri.replace("sqlite:///", "")
                if db_path and os.path.exists(db_path):
                    import os

                    os.remove(db_path)
                    if os.path.exists(db_path + "-journal"):
                        os.remove(db_path + "-journal")
                    # Retry
                    mlflow.set_tracking_uri(tracking_uri)
                    mlflow.create_experiment(experiment_name)
        else:
            # Experiment might already exist
            pass
    mlflow.set_experiment(experiment_name)


@contextmanager
def mlflow_run(
    run_name: str | None = None,
    tags: dict[str, str] | None = None,
    log_system_info: bool = True,
):
    """Context manager for MLflow runs.

    Args:
        run_name: Name of the run
        tags: Tags to add to the run
        log_system_info: Whether to log system information
    """
    with mlflow.start_run(run_name=run_name, tags=tags):
        if log_system_info:
            import platform
            import sys

            mlflow.log_param("python_version", sys.version)
            mlflow.log_param("platform", platform.platform())

        yield


def log_experiment_summary(
    experiment_name: str = "iris-classification",
    tracking_uri: str = "sqlite:///mlflow.db",
) -> dict[str, Any]:
    """Get summary of all experiments.

    Args:
        experiment_name: Name of the experiment
        tracking_uri: URI for MLflow tracking

    Returns:
        Dictionary with experiment summary
    """
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        return {"error": "Experiment not found"}

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],
    )

    summary: dict[str, Any] = {
        "total_runs": len(runs),
        "best_accuracy": 0.0,
        "runs": [],
    }

    for run in runs:
        run_info: dict[str, Any] = {
            "run_id": run.info.run_id,
            "run_name": run.info.run_name,
            "status": run.info.status,
            "accuracy": run.data.metrics.get("accuracy", 0.0),
            "algorithm": run.data.params.get("algorithm")
            or run.data.tags.get("algorithm", "unknown"),
        }
        summary["runs"].append(run_info)
        if run_info["accuracy"] > summary["best_accuracy"]:
            summary["best_accuracy"] = run_info["accuracy"]

    return summary


def compare_experiments(
    experiment_name: str = "iris-classification",
    tracking_uri: str = "sqlite:///mlflow.db",
    metric: str = "accuracy",
    top_n: int = 5,
) -> None:
    """Compare top N experiments.

    Args:
        experiment_name: Name of the experiment
        tracking_uri: URI for MLflow tracking
        metric: Metric to compare
        top_n: Number of top experiments to show
    """
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print("❌ Experiment not found")
        return

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric} DESC"],
        max_results=top_n,
    )

    print(f"\n🏆 Top {top_n} experiments by {metric}:\n")
    print(f"{'Algorithm':<20} {'Accuracy':<12} {'Run ID':<40}")
    print("-" * 75)

    for run in runs:
        algorithm = run.data.params.get("algorithm") or run.data.tags.get("algorithm", "unknown")
        accuracy = run.data.metrics.get(metric, 0.0)
        run_id = run.info.run_id[:40]
        print(f"{algorithm:<20} {accuracy:<12.4f} {run_id:<40}")
