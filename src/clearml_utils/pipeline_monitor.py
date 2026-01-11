"""ClearML pipeline monitoring and notification utilities using ClearML API."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from clearml import PipelineController, Task

logger = logging.getLogger(__name__)


class ClearMLPipelineMonitor:
    """Monitor ClearML pipeline execution using ClearML API."""

    def __init__(self):
        """Initialize monitor."""
        self.logger = logging.getLogger("clearml_pipeline_monitor")
        self.logger.setLevel(logging.INFO)

    def monitor_pipeline(
        self,
        pipeline_id: str,
        check_interval: int = 10,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Monitor pipeline execution with periodic checks using ClearML API.

        Args:
            pipeline_id: ID of the pipeline task
            check_interval: Interval between checks in seconds
            timeout: Maximum time to wait in seconds (None for no timeout)

        Returns:
            Dictionary with final pipeline status
        """
        start_time = time.time()
        self.logger.info(f"🔍 Starting monitoring for pipeline: {pipeline_id}")

        while True:
            try:
                # Get pipeline status from ClearML
                status = self.get_pipeline_status(pipeline_id)
                current_status = status.get("status", "unknown")

                self.logger.info(f"📊 Pipeline status: {current_status}")

                # Log to ClearML task
                try:
                    task = Task.get_task(task_id=pipeline_id)
                    task.logger.report_text(
                        f"Pipeline monitoring: status={current_status} at {datetime.now().isoformat()}"
                    )
                except Exception:
                    pass

                # Check if pipeline is completed or failed
                if current_status in ["completed", "failed", "stopped", "closed"]:
                    self.logger.info(f"✅ Pipeline finished with status: {current_status}")
                    return status

                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    self.logger.warning(f"⏱️ Monitoring timeout after {timeout}s")
                    return {
                        "id": pipeline_id,
                        "status": "timeout",
                        "message": f"Monitoring timeout after {timeout}s",
                    }

                # Wait before next check
                time.sleep(check_interval)

            except Exception as e:
                self.logger.error(f"❌ Error monitoring pipeline: {e}")
                return {"id": pipeline_id, "status": "error", "error": str(e)}

    def get_pipeline_status(self, pipeline_id: str) -> dict[str, Any]:
        """Get detailed status of pipeline from ClearML API.

        Args:
            pipeline_id: ID of the pipeline task

        Returns:
            Dictionary with detailed pipeline status including steps
        """
        try:
            task = Task.get_task(task_id=pipeline_id)

            # Get pipeline controller to access steps
            pipeline_controller = None
            try:
                pipeline_controller = PipelineController.from_task_id(pipeline_id)
            except Exception:
                # If we can't get controller, just use task info
                pass

            # Get step statuses
            steps_status = []
            if pipeline_controller:
                try:
                    for step in pipeline_controller.steps:
                        step_status = {
                            "name": step.name,
                            "status": getattr(step, "status", "unknown"),
                            "task_id": getattr(step, "task_id", None),
                        }
                        steps_status.append(step_status)
                except Exception as e:
                    logger.warning(f"Could not get step statuses: {e}")

            # Calculate duration
            duration = None
            if hasattr(task, "started") and hasattr(task, "completed"):
                if task.started and task.completed:
                    duration = (task.completed - task.started).total_seconds()
                elif task.started:
                    # Still running
                    duration = (datetime.now() - task.started).total_seconds()

            status = {
                "id": task.id,
                "name": task.name,
                "status": task.status,
                "created": str(task.created) if hasattr(task, "created") and task.created else None,
                "started": str(task.started) if hasattr(task, "started") and task.started else None,
                "completed": str(task.completed)
                if hasattr(task, "completed") and task.completed
                else None,
                "duration": duration,
                "steps": steps_status,
                "project": getattr(task, "project", "EPML"),
                "url": f"http://localhost:8080/projects/{getattr(task, 'project', 'EPML')}/experiments/{task.id}",
            }

            return status
        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return {
                "id": pipeline_id,
                "status": "error",
                "error": str(e),
            }

    def get_pipeline_summary(self, pipeline_id: str) -> dict[str, Any]:
        """Get summary of pipeline execution from ClearML.

        Args:
            pipeline_id: ID of the pipeline task

        Returns:
            Dictionary with pipeline summary
        """
        return self.get_pipeline_status(pipeline_id)

    def log_pipeline_progress(self, pipeline_id: str, message: str):
        """Log progress message to ClearML pipeline task.

        Args:
            pipeline_id: ID of the pipeline task
            message: Progress message
        """
        try:
            task = Task.get_task(task_id=pipeline_id)
            task.logger.report_text(f"[Monitor] {datetime.now().isoformat()}: {message}")
        except Exception as e:
            logger.warning(f"Could not log to ClearML: {e}")

    def send_notification_to_clearml(
        self,
        pipeline_id: str,
        status: str,
        summary: dict[str, Any],
    ):
        """Send notification about pipeline completion to ClearML task.

        Args:
            pipeline_id: ID of the pipeline task
            status: Pipeline status (success, failed, etc.)
            summary: Pipeline summary dictionary
        """
        try:
            task = Task.get_task(task_id=pipeline_id)

            # Create notification message
            status_emoji = "✅" if status == "completed" else "❌"
            notification_text = f"""
{status_emoji} Pipeline {status.upper()}

Summary:
- Duration: {summary.get('duration', 'N/A')}s
- Steps: {len(summary.get('steps', []))}
- Status: {summary.get('status', 'unknown')}

View at: {summary.get('url', 'N/A')}
"""

            # Log to ClearML task
            task.logger.report_text(notification_text)

            # Add as task comment/description
            try:
                current_description = getattr(task, "data", {}).get("comment", "") or ""
                new_description = f"{current_description}\n\n{notification_text}"
                task.set_comment(new_description)
            except Exception:
                pass

            # Set task tags
            try:
                tags = list(task.get_tags() or [])
                tags.append(f"monitored_{status}")
                task.set_tags(tags)
            except Exception:
                pass

            logger.info(f"📧 Notification sent to ClearML task: {pipeline_id}")

        except Exception as e:
            logger.error(f"❌ Failed to send notification to ClearML: {e}")


def send_notification(
    pipeline_id: str,
    status: str,
    summary: dict[str, Any],
    output_file: str | None = None,
) -> dict[str, Any]:
    """Send notification about pipeline completion via ClearML.

    Args:
        pipeline_id: ID of the pipeline task
        status: Pipeline status (success, failed, etc.)
        summary: Pipeline summary dictionary
        output_file: Optional local file to save notification (for backup)

    Returns:
        Notification dictionary
    """
    monitor = ClearMLPipelineMonitor()

    # Send notification to ClearML
    monitor.send_notification_to_clearml(pipeline_id, status, summary)

    # Also save locally if requested
    if output_file:
        notification = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_id": pipeline_id,
            "status": status,
            "summary": summary,
            "url": summary.get(
                "url",
                f"http://localhost:8080/projects/{summary.get('project', 'EPML')}/experiments/{pipeline_id}",
            ),
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(notification, f, indent=2, default=str)

        logger.info(f"📧 Notification also saved to: {output_file}")

    # Print notification
    status_emoji = "✅" if status == "completed" else "❌"
    print(f"\n{status_emoji} ClearML Pipeline {status.upper()}")
    print(f"Pipeline ID: {pipeline_id}")
    print(f"Duration: {summary.get('duration', 'N/A')}s")
    print(f"Steps: {len(summary.get('steps', []))}")
    print(f"View at: {summary.get('url', 'N/A')}")
    print("📧 Notification sent to ClearML task")

    return {
        "pipeline_id": pipeline_id,
        "status": status,
        "sent_to_clearml": True,
    }
