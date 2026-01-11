"""Script to compare and filter experiments."""

import mlflow
from mlflow.tracking import MlflowClient

from src.utils.mlflow_utils import compare_experiments, log_experiment_summary


def filter_experiments(
    experiment_name: str = "iris-classification",
    tracking_uri: str = "sqlite:///mlflow.db",
    min_accuracy: float = 0.0,
    algorithm: str | None = None,
    max_results: int = 20,
):
    """Filter experiments by criteria.

    Args:
        experiment_name: Name of the experiment
        tracking_uri: URI for MLflow tracking
        min_accuracy: Minimum accuracy threshold
        algorithm: Filter by algorithm name (optional)
        max_results: Maximum number of results
    """
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print("❌ Experiment not found")
        return

    # Build filter string
    filter_string = f"metrics.accuracy >= {min_accuracy}"
    if algorithm:
        # Try to filter by algorithm (check both params and tags)
        # Note: MLflow filter syntax doesn't support OR easily, so we'll filter in Python
        filter_string = f"metrics.accuracy >= {min_accuracy}"

    runs_list = list(
        client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=filter_string,
            order_by=["metrics.accuracy DESC"],
            max_results=max_results * 2,  # Get more to filter by algorithm
        )
    )

    # Filter by algorithm if specified
    if algorithm:
        runs_list = [
            run
            for run in runs_list
            if (
                run.data.params.get("algorithm") == algorithm
                or run.data.tags.get("algorithm") == algorithm
            )
        ]

    runs = runs_list[:max_results]  # Limit results

    print(f"\n🔍 Found {len(runs)} experiments matching criteria:")
    print(f"   Min accuracy: {min_accuracy}")
    if algorithm:
        print(f"   Algorithm: {algorithm}")
    print()

    print(f"{'Algorithm':<25} {'Accuracy':<12} {'Train Acc':<12} {'Run ID':<40}")
    print("-" * 95)

    for run in runs:
        # Try to get algorithm from params first, then from tags
        alg = run.data.params.get("algorithm") or run.data.tags.get("algorithm", "unknown")
        acc = run.data.metrics.get("accuracy", 0.0)
        train_acc = run.data.metrics.get("train_accuracy", 0.0)
        run_id = run.info.run_id[:40]
        print(f"{alg:<25} {acc:<12.4f} {train_acc:<12.4f} {run_id:<40}")


def main():
    """Main function to compare experiments."""
    import json
    from pathlib import Path

    tracking_uri = "sqlite:///mlflow.db"
    experiment_name = "iris-classification"

    print("=" * 80)
    print("📊 Experiment Comparison and Analysis")
    print("=" * 80)

    # Get summary
    print("\n1️⃣ Experiment Summary:")
    summary = log_experiment_summary(experiment_name, tracking_uri)
    if "error" not in summary:
        print(f"   Total runs: {summary['total_runs']}")
        print(f"   Best accuracy: {summary['best_accuracy']:.4f}")

    # Compare top experiments
    print("\n2️⃣ Top 10 Experiments:")
    compare_experiments(experiment_name, tracking_uri, metric="accuracy", top_n=10)

    # Filter experiments
    print("\n3️⃣ Filtered Experiments (accuracy >= 0.95):")
    filter_experiments(experiment_name, tracking_uri, min_accuracy=0.95)

    print("\n4️⃣ Filtered Experiments (RandomForest only):")
    filter_experiments(experiment_name, tracking_uri, algorithm="RandomForest")

    # Save comparison results
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    comparison_file = metrics_dir / "comparison_results.json"

    comparison_data = {
        "summary": summary,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    with open(comparison_file, "w") as f:
        json.dump(comparison_data, f, indent=2)

    print(f"\n✅ Comparison results saved to {comparison_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
