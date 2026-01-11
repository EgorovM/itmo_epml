"""Script to reset MLflow database if there are migration errors."""

from pathlib import Path


def reset_mlflow_db(db_path: str = "mlflow.db"):
    """Reset MLflow database by removing old files.

    Args:
        db_path: Path to SQLite database file
    """
    db_file = Path(db_path)
    journal_file = Path(f"{db_path}-journal")

    if db_file.exists():
        db_file.unlink()
        print(f"✅ Removed {db_file}")

    if journal_file.exists():
        journal_file.unlink()
        print(f"✅ Removed {journal_file}")

    if not db_file.exists() and not journal_file.exists():
        print("✅ Database reset complete. MLflow will create a new database on next run.")
    else:
        print("⚠️ Some files could not be removed.")


if __name__ == "__main__":
    reset_mlflow_db()
