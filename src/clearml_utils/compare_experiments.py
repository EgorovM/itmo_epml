"""Compare ClearML experiments."""

import logging

from src.clearml_utils.tracking import compare_experiments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Compare experiments in ClearML."""
    logger.info("📊 Comparing ClearML experiments...")

    experiments = compare_experiments(
        project_name="EPML",
        metric="accuracy",
        top_n=10,
    )

    print("\n" + "=" * 80)
    print("🏆 Top Experiments by Accuracy")
    print("=" * 80)
    print(f"{'Algorithm':<25} {'Accuracy':<12} {'Task ID':<40}")
    print("-" * 80)

    for exp in experiments:
        algorithm = exp.get("parameters", {}).get("algorithm", "unknown")
        accuracy = exp.get("metric")
        accuracy_str = f"{accuracy:.4f}" if accuracy is not None else "N/A"
        task_id = exp.get("task_id", "unknown")
        print(f"{algorithm:<25} {accuracy_str:<12} {task_id:<40}")

    print("=" * 80)


if __name__ == "__main__":
    main()
