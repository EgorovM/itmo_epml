"""Script to compare different model versions using MLflow."""

import mlflow
from mlflow.tracking import MlflowClient


def compare_models():
    """Compare different model versions and display comparison results."""
    # Set up MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    client = MlflowClient()

    # Get experiment
    experiment = mlflow.get_experiment_by_name("iris_classification")
    if experiment is None:
        print("❌ No experiment found. Please train a model first.")
        return

    # Get all runs
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],
    )

    if not runs:
        print("❌ No runs found in the experiment.")
        return

    print(f"\n{'='*80}")
    print(f"Model Comparison - Experiment: {experiment.name}")
    print(f"{'='*80}\n")

    # Display runs
    for i, run in enumerate(runs, 1):
        print(f"Run #{i}: {run.info.run_id}")
        print(f"  Status: {run.info.status}")
        print(f"  Start Time: {run.info.start_time}")
        print("  Parameters:")
        for key, value in run.data.params.items():
            print(f"    {key}: {value}")
        print("  Metrics:")
        for key, value in run.data.metrics.items():
            print(f"    {key}: {value:.4f}")
        print()

    # Compare best runs
    if len(runs) > 1:
        best_run = runs[0]
        second_best = runs[1] if len(runs) > 1 else None

        print(f"{'='*80}")
        print("Best Model:")
        print(f"  Run ID: {best_run.info.run_id}")
        print(f"  Accuracy: {best_run.data.metrics.get('accuracy', 'N/A'):.4f}")
        print(f"  Parameters: {best_run.data.params}")

        if second_best:
            accuracy_diff = best_run.data.metrics.get("accuracy", 0) - second_best.data.metrics.get(
                "accuracy", 0
            )
            print(f"\n  Improvement over 2nd best: {accuracy_diff:.4f}")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    compare_models()
