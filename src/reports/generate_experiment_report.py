"""Generate experiment reports in Markdown format."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import mlflow
from mlflow.tracking import MlflowClient

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
) -> list[dict]:
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


def generate_comparison_table(experiments: list[dict]) -> str:
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

    table = "| Algorithm | Accuracy | Train Accuracy | Status |\n"
    table += "|-----------|----------|----------------|--------|\n"

    for exp in sorted_experiments[:20]:  # Top 20
        algorithm = exp.get("algorithm", "unknown")
        accuracy = exp.get("accuracy", 0.0)
        train_acc = exp.get("train_accuracy", 0.0)
        status = exp.get("status", "unknown")
        table += f"| {algorithm} | {accuracy:.4f} | {train_acc:.4f} | {status} |\n"

    return table


def generate_experiment_report(
    output_file: str = "reports/experiment_report.md",
    experiment_name: str = "iris-classification",
) -> None:
    """Generate experiment report in Markdown format.

    Args:
        output_file: Output file path
        experiment_name: Name of the experiment
    """
    logger.info(f"Generating experiment report: {output_file}")

    # Load experiments
    experiments = load_mlflow_experiments(experiment_name)

    if not experiments:
        logger.warning("No experiments found")
        return

    # Generate report
    report = f"""# Experiment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Experiment:** {experiment_name}
**Total Experiments:** {len(experiments)}

## Summary

- **Total Runs:** {len(experiments)}
- **Best Accuracy:** {max(exp.get('accuracy', 0.0) for exp in experiments):.4f}
- **Average Accuracy:** {sum(exp.get('accuracy', 0.0) for exp in experiments) / len(experiments):.4f}

## Top Experiments

{generate_comparison_table(experiments)}

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
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    logger.info(f"✅ Report saved to {output_file}")


if __name__ == "__main__":
    generate_experiment_report()
