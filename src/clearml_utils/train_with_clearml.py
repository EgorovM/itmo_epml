"""Training script with ClearML tracking."""

import json
import logging
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from src.clearml_utils.setup import setup_clearml
from src.clearml_utils.tracking import log_artifacts, log_metrics, log_model, log_parameters

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_data(data_path: str = "data/processed/iris_processed.csv"):
    """Load and prepare data."""
    data_file = Path(data_path)
    if data_file.exists():
        df = pd.read_csv(data_file)
        X = df.drop(["target", "target_name"], axis=1).values
        y = df["target"].values
        logger.info(f"✅ Loaded data from {data_file}")
    else:
        from sklearn.datasets import load_iris

        iris = load_iris()
        X, y = iris.data, iris.target
        logger.info("✅ Loaded data from sklearn")

    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_model(
    algorithm_name: str,
    model,
    X_train,
    X_test,
    y_train,
    y_test,
    params: dict,
):
    """Train model with ClearML tracking.

    Args:
        algorithm_name: Name of the algorithm
        model: sklearn model instance
        X_train: Training features
        X_test: Test features
        y_train: Training labels
        y_test: Test labels
        params: Model parameters

    Returns:
        Accuracy score
    """
    task = None
    try:
        # Setup ClearML task for this experiment
        task = setup_clearml(
            project_name="EPML",
            task_name=f"{algorithm_name}_training",
            tags=[algorithm_name, "iris", "classification"],
        )

        # Log parameters
        log_parameters(params, task)

        # Train model
        logger.info(f"Training {algorithm_name}...")
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        train_accuracy = model.score(X_train, y_train)

        # Log metrics as scalars
        log_metrics(
            {
                "accuracy": accuracy,
                "train_accuracy": train_accuracy,
            },
            task=task,
        )

        # Log confusion matrix as plot
        try:
            cm = confusion_matrix(y_test, y_pred)
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_title(f"Confusion Matrix - {algorithm_name}")
            ax.set_ylabel("True Label")
            ax.set_xlabel("Predicted Label")

            # Log plot to ClearML
            task.logger.report_matplotlib_figure(
                title="Confusion Matrix",
                series=algorithm_name,
                iteration=0,
                figure=fig,
            )
            plt.close(fig)
        except Exception as e:
            logger.warning(f"Could not log confusion matrix: {e}")

        # Save model
        models_dir = Path("models")
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / f"{algorithm_name.lower()}_clearml.pkl"
        joblib.dump(model, model_path, compress=True)

        # Register model in ClearML
        model_registry = log_model(
            str(model_path),
            f"{algorithm_name}_iris",
            tags=[algorithm_name, "iris"],
            task=task,
            metadata={
                "accuracy": float(accuracy),
                "train_accuracy": float(train_accuracy),
                "algorithm": algorithm_name,
            },
            model_object=model,
        )

        # Save metrics
        metrics_dir = Path("metrics")
        metrics_dir.mkdir(parents=True, exist_ok=True)
        metrics_data = {
            "accuracy": float(accuracy),
            "train_accuracy": float(train_accuracy),
            "algorithm": algorithm_name,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }
        metrics_file = metrics_dir / f"{algorithm_name.lower()}_clearml_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)

        # Log artifacts
        log_artifacts(
            {
                "model": str(model_path),
                "metrics": str(metrics_file),
            },
            task=task,
        )

        logger.info(f"✅ Model trained with accuracy: {accuracy:.4f}")
        logger.info(f"✅ Model registered: {model_registry.id}")

        # Mark as completed and close task
        try:
            task.mark_completed()
        except Exception:
            pass
        finally:
            task.close()

        return accuracy
    except Exception as e:
        # Mark task as failed if there was an error
        if task is not None:
            try:
                task.mark_failed(str(e))
            except Exception:
                pass
            finally:
                task.close()
        raise
