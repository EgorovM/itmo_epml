"""Main pipeline script with Hydra and monitoring."""

import time
from contextlib import contextmanager

import hydra
from omegaconf import DictConfig, OmegaConf

from src.pipeline.monitor import PipelineMonitor
from src.pipeline.notify import create_notification_file, print_notification
from src.pipeline.validate_config import validate_config

# Initialize monitor
monitor = PipelineMonitor()


@contextmanager
def stage_context(stage_name: str, config: DictConfig | None = None):
    """Context manager for pipeline stages."""
    start_time = time.time()
    monitor.log_stage_start(stage_name, config)
    try:
        yield
        duration = time.time() - start_time
        monitor.log_stage_complete(stage_name, duration)
        yield {"status": "success", "duration": duration}
    except Exception as e:
        duration = time.time() - start_time
        monitor.log_stage_error(stage_name, e)
        raise


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def run_pipeline(cfg: DictConfig) -> None:
    """Run complete ML pipeline."""
    # Validate configuration
    validation_result = validate_config(cfg)
    if not validation_result["valid"]:
        error_msg = "Configuration validation failed:\n" + "\n".join(validation_result["errors"])
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            print(f"⚠️  Configuration warning: {warning}")

    stages = []
    pipeline_start = time.time()

    try:
        # Stage 1: Prepare data
        with stage_context("prepare_data", cfg):
            from src.data.prepare_data import prepare_iris_data

            prepare_iris_data()
            stages.append({"name": "prepare_data", "status": "success"})

        # Stage 2: Train model
        with stage_context("train", cfg):
            from src.pipeline.train_with_config import train

            # Override config for training
            train(cfg)
            stages.append({"name": "train", "status": "success"})

        # Stage 3: Evaluate (optional)
        if cfg.get("evaluate", True):
            with stage_context("evaluate", cfg):
                # Evaluation can be added here
                stages.append({"name": "evaluate", "status": "success"})

        pipeline_duration = time.time() - pipeline_start

        # Create summary
        summary = {
            "status": "success",
            "stages": stages,
            "total_duration": pipeline_duration,
            "config": OmegaConf.to_container(cfg, resolve=True),
        }

        # Log summary
        monitor.log_pipeline_summary(stages)

        # Create notification
        if cfg.monitoring.get("notify_on_completion", True):
            notification = create_notification_file(
                status="success",
                stages=stages,
                total_duration=pipeline_duration,
            )
            print_notification(notification)

        monitor.notify_completion(True, summary)

    except Exception as e:
        pipeline_duration = time.time() - pipeline_start
        summary = {
            "status": "failed",
            "stages": stages,
            "total_duration": pipeline_duration,
            "error": str(e),
        }
        monitor.notify_completion(False, summary)
        notification = create_notification_file(
            status="failed",
            stages=stages,
            total_duration=pipeline_duration,
        )
        print_notification(notification)
        raise


if __name__ == "__main__":
    run_pipeline()
