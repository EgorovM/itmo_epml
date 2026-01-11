"""Notification utilities for pipeline completion."""

import json
from datetime import datetime
from pathlib import Path


def create_notification_file(
    status: str,
    stages: list[dict],
    total_duration: float,
    output_file: str = "logs/pipeline_notification.json",
) -> dict:
    """Create notification file with pipeline results.

    Args:
        status: Pipeline status (success/failed)
        stages: List of stage results
        total_duration: Total pipeline duration
        output_file: Output file path

    Returns:
        Notification dictionary
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    notification = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "stages": stages,
        "total_duration": total_duration,
        "summary": {
            "total_stages": len(stages),
            "successful": len([s for s in stages if s.get("status") == "success"]),
            "failed": len([s for s in stages if s.get("status") == "error"]),
        },
    }

    with open(output_path, "w") as f:
        json.dump(notification, f, indent=2)

    return notification


def print_notification(notification: dict):
    """Print notification to console.

    Args:
        notification: Notification dictionary
    """
    status_emoji = "✅" if notification["status"] == "success" else "❌"
    print(f"\n{status_emoji} Pipeline {notification['status'].upper()}")
    print(f"Duration: {notification['total_duration']:.2f}s")
    print(
        f"Stages: {notification['summary']['successful']}/{notification['summary']['total_stages']} successful"
    )
    print("Notification saved to: logs/pipeline_notification.json")
