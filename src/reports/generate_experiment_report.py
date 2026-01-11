"""Generate experiment reports in Markdown format with visualizations."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import seaborn as sns
from mlflow.tracking import MlflowClient

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_metrics_from_file(
    metrics_file: str = "metrics/experiments_summary.json",
) -> list[dict[str, Any]]:
    """Load metrics from JSON file.

    Args:
        metrics_file: Path to metrics file

    Returns:
        List of experiment metrics
    """
    metrics_path = Path(metrics_file)
    if not metrics_path.exists():
        logger.warning(f"Metrics file not found: {metrics_file}")
        return []

    with open(metrics_path) as f:
        data = json.load(f)
        return list(data) if isinstance(data, list) else []


def load_mlflow_experiments(
    experiment_name: str = "iris-classification",
    tracking_uri: str = "sqlite:///mlflow.db",
) -> list[dict[str, Any]]:
    """Load experiments from MLflow.

    Args:
        experiment_name: Name of the experiment
        tracking_uri: MLflow tracking URI

    Returns:
        List of experiment data
    """
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        logger.warning(f"Experiment not found: {experiment_name}")
        return []

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],
    )

    experiments = []
    for run in runs:
        experiments.append(
            {
                "run_id": run.info.run_id,
                "run_name": run.info.run_name,
                "status": run.info.status,
                "accuracy": run.data.metrics.get("accuracy", 0.0),
                "train_accuracy": run.data.metrics.get("train_accuracy", 0.0),
                "algorithm": run.data.params.get("algorithm")
                or run.data.tags.get("algorithm", "unknown"),
                "parameters": dict(run.data.params),
            }
        )

    return experiments


def generate_comparison_table(experiments: list[dict[str, Any]]) -> str:
    """Generate comparison table in Markdown format.

    Args:
        experiments: List of experiment data

    Returns:
        Markdown table string
    """
    if not experiments:
        return "No experiments found."

    # Sort by accuracy
    sorted_experiments = sorted(experiments, key=lambda x: x.get("accuracy", 0.0), reverse=True)

    table = "| Rank | Algorithm | Accuracy | Train Accuracy | Status |\n"
    table += "|------|-----------|----------|----------------|--------|\n"

    for rank, exp in enumerate(sorted_experiments[:20], 1):  # Top 20
        algorithm = exp.get("algorithm", "unknown")
        accuracy = exp.get("accuracy", 0.0)
        train_acc = exp.get("train_accuracy", 0.0)
        status = exp.get("status", "unknown")
        table += f"| {rank} | {algorithm} | {accuracy:.4f} | {train_acc:.4f} | {status} |\n"

    return table


def generate_visualizations(experiments: list[dict[str, Any]], output_dir: Path) -> list[str]:
    """Generate visualizations for experiments.

    Args:
        experiments: List of experiment data
        output_dir: Directory to save plots

    Returns:
        List of plot file paths
    """
    if not experiments:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_files = []

    # Prepare data
    df = pd.DataFrame(experiments)
    df = df.sort_values("accuracy", ascending=False)

    # 1. Accuracy comparison bar plot
    plt.figure(figsize=(12, 6))
    top_10 = df.head(10)
    plt.barh(range(len(top_10)), top_10["accuracy"], color="steelblue")
    plt.yticks(range(len(top_10)), top_10["algorithm"])
    plt.xlabel("Accuracy")
    plt.title("Top 10 Models by Accuracy")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    accuracy_plot = output_dir / "accuracy_comparison.png"
    plt.savefig(accuracy_plot, dpi=150, bbox_inches="tight")
    plt.close()
    plot_files.append(str(accuracy_plot))

    # 2. Train vs Test accuracy scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(df["train_accuracy"], df["accuracy"], alpha=0.6, s=100)
    for _, row in df.iterrows():
        plt.annotate(
            row["algorithm"],
            (row["train_accuracy"], row["accuracy"]),
            fontsize=8,
            alpha=0.7,
        )
    plt.xlabel("Train Accuracy")
    plt.ylabel("Test Accuracy")
    plt.title("Train vs Test Accuracy")
    plt.plot([0, 1], [0, 1], "r--", alpha=0.3, label="y=x")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    scatter_plot = output_dir / "train_vs_test.png"
    plt.savefig(scatter_plot, dpi=150, bbox_inches="tight")
    plt.close()
    plot_files.append(str(scatter_plot))

    # 3. Accuracy distribution histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df["accuracy"], bins=20, edgecolor="black", alpha=0.7, color="steelblue")
    plt.xlabel("Accuracy")
    plt.ylabel("Number of Experiments")
    plt.title("Distribution of Accuracy Scores")
    mean_acc = df["accuracy"].mean()
    plt.axvline(mean_acc, color="red", linestyle="--", label=f"Mean: {mean_acc:.4f}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    hist_plot = output_dir / "accuracy_distribution.png"
    plt.savefig(hist_plot, dpi=150, bbox_inches="tight")
    plt.close()
    plot_files.append(str(hist_plot))

    return plot_files


def generate_experiment_report(
    output_file: str = "docs/reports/experiment_report.md",
    experiment_name: str = "iris-classification",
    include_plots: bool = True,
) -> None:
    """Generate experiment report in Markdown format with visualizations.

    Args:
        output_file: Output file path
        experiment_name: Name of the experiment
        include_plots: Whether to generate plots
    """
    logger.info(f"Generating experiment report: {output_file}")

    # Load experiments
    experiments = load_mlflow_experiments(experiment_name)

    if not experiments:
        logger.warning("No experiments found")
        return

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plots_dir = output_path.parent / "figures"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    plot_files = []
    if include_plots:
        logger.info("Generating visualizations...")
        plot_files = generate_visualizations(experiments, plots_dir)
        logger.info(f"✅ Generated {len(plot_files)} plots")

    # Calculate statistics
    accuracies = [exp.get("accuracy", 0.0) for exp in experiments]

    # Generate report
    report = f"""# Experiment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Experiment:** {experiment_name}
**Total Experiments:** {len(experiments)}

## Summary

- **Total Runs:** {len(experiments)}
- **Best Accuracy:** {max(accuracies):.4f}
- **Average Accuracy:** {sum(accuracies) / len(accuracies):.4f}
- **Min Accuracy:** {min(accuracies):.4f}
- **Std Deviation:** {pd.Series(accuracies).std():.4f}

## Visualizations

"""

    # Add plot references
    if plot_files:
        report += "### Accuracy Comparison\n\n"
        report += "![Accuracy Comparison](figures/accuracy_comparison.png)\n\n"
        report += "### Train vs Test Accuracy\n\n"
        report += "![Train vs Test](figures/train_vs_test.png)\n\n"
        report += "### Accuracy Distribution\n\n"
        report += "![Accuracy Distribution](figures/accuracy_distribution.png)\n\n"

    report += """## Comparison Table

"""

    report += generate_comparison_table(experiments)

    report += """

## Detailed Results

"""

    # Add detailed results
    for i, exp in enumerate(
        sorted(experiments, key=lambda x: x.get("accuracy", 0.0), reverse=True)[:10], 1
    ):
        report += f"""
### {i}. {exp.get('algorithm', 'unknown')}

- **Accuracy:** {exp.get('accuracy', 0.0):.4f}
- **Train Accuracy:** {exp.get('train_accuracy', 0.0):.4f}
- **Status:** {exp.get('status', 'unknown')}
- **Run ID:** `{exp.get('run_id', 'unknown')[:8]}`

**Parameters:**
```yaml
{json.dumps(exp.get('parameters', {}), indent=2, default=str)}
```

"""

    # Save report
    with open(output_path, "w") as f:
        f.write(report)

    logger.info(f"✅ Report saved to {output_path}")
    if plot_files:
        logger.info(f"✅ Plots saved to {plots_dir}")


if __name__ == "__main__":
    generate_experiment_report()
