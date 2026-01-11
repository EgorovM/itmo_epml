"""Run pipeline for all model configurations."""

import subprocess
import sys

from src.pipeline.monitor import PipelineMonitor

monitor = PipelineMonitor()


def run_model_pipeline(model_name: str) -> dict:
    """Run pipeline for a specific model.

    Args:
        model_name: Name of the model configuration

    Returns:
        Dictionary with execution results
    """
    cmd = [
        sys.executable,
        "src/pipeline/train_with_config.py",
        f"model={model_name}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "model": model_name,
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {
            "model": model_name,
            "status": "error",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
        }


def main():
    """Run pipeline for all model configurations."""
    models = ["random_forest", "svm", "logistic_regression", "knn"]

    monitor.logger.info("🚀 Starting parallel model training")
    monitor.logger.info(f"Models to train: {models}")

    results = []
    for model in models:
        monitor.log_stage_start(f"train_{model}")
        result = run_model_pipeline(model)
        results.append(result)

        if result["status"] == "success":
            monitor.log_stage_complete(f"train_{model}", 0.0)
        else:
            monitor.log_stage_error(
                f"train_{model}", Exception(result.get("stderr", "Unknown error"))
            )

    # Summary
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    monitor.logger.info("=" * 80)
    monitor.logger.info("📊 Pipeline Execution Summary")
    monitor.logger.info("=" * 80)
    monitor.logger.info(f"Total models: {len(models)}")
    monitor.logger.info(f"Successful: {len(successful)}")
    monitor.logger.info(f"Failed: {len(failed)}")

    for result in results:
        status = "✅" if result["status"] == "success" else "❌"
        monitor.logger.info(f"{status} {result['model']}")

    return results


if __name__ == "__main__":
    main()
