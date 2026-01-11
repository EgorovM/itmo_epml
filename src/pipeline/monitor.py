"""Pipeline monitoring utilities."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from omegaconf import DictConfig


class PipelineMonitor:
    """Monitor pipeline execution."""

    def __init__(self, log_file: str = "logs/pipeline.log"):
        """Initialize monitor.

        Args:
            log_file: Path to log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup file logger
        self.logger = logging.getLogger("pipeline_monitor")
        self.logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(console_handler)

    def log_stage_start(self, stage: str, config: DictConfig | None = None):
        """Log start of pipeline stage."""
        self.logger.info(f"🚀 Starting stage: {stage}")
        if config:
            self.logger.info(f"Configuration: {config}")

    def log_stage_complete(
        self, stage: str, duration: float, metrics: dict[str, Any] | None = None
    ):
        """Log completion of pipeline stage."""
        self.logger.info(f"✅ Completed stage: {stage} (duration: {duration:.2f}s)")
        if metrics:
            self.logger.info(f"Metrics: {metrics}")

    def log_stage_error(self, stage: str, error: Exception):
        """Log error in pipeline stage."""
        self.logger.error(f"❌ Error in stage {stage}: {error}")

    def log_pipeline_summary(self, stages: list[dict[str, Any]]):
        """Log pipeline execution summary."""
        total_duration = sum(s.get("duration", 0) for s in stages)
        self.logger.info("=" * 80)
        self.logger.info("📊 Pipeline Execution Summary")
        self.logger.info("=" * 80)
        self.logger.info(f"Total stages: {len(stages)}")
        self.logger.info(f"Total duration: {total_duration:.2f}s")
        for stage in stages:
            status = "✅" if stage.get("status") == "success" else "❌"
            self.logger.info(f"{status} {stage['name']}: {stage.get('duration', 0):.2f}s")
        self.logger.info("=" * 80)

    def notify_completion(self, success: bool, summary: dict[str, Any]):
        """Notify about pipeline completion."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"{status} - Pipeline completed")
        self.logger.info(f"Summary: {json.dumps(summary, indent=2)}")


def create_notification(summary: dict[str, Any], output_file: str = "logs/pipeline_summary.json"):
    """Create notification file with pipeline summary."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    notification = {
        "timestamp": datetime.now().isoformat(),
        "status": summary.get("status", "unknown"),
        "stages": summary.get("stages", []),
        "total_duration": summary.get("total_duration", 0),
    }

    with open(output_path, "w") as f:
        json.dump(notification, f, indent=2)

    return notification
