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
    # Check if task already exists (when executed by pipeline/agent)
    from clearml import Task

    task = Task.current_task()
    task_created = False

    if task is None:
        # Create new task only if not executed by agent/pipeline
        task = setup_clearml(
            project_name="EPML",
            task_name=f"{algorithm_name}_training",
            tags=[algorithm_name, "iris", "classification"],
        )
        task_created = True
        logger.info(f"📝 Created new ClearML task: {task.id}")
    else:
        logger.info(f"📋 Using existing ClearML task: {task.id} (from pipeline/agent)")

    try:
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

        try:
            task.mark_completed()
            logger.info(f"✅ Task {task.id} marked as completed")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not mark task as completed: {e}")
            try:
                task.flush()
            except Exception:
                pass

        if task_created:
            try:
                task.close()
                logger.info("✅ Task closed (we created it)")
            except Exception as e:
                logger.warning(f"⚠️ Could not close task: {e}")
        else:
            logger.info("ℹ️ Task not closed (managed by pipeline)")

        return accuracy
    except Exception as e:
        # Mark task as failed if there was an error
        if task is not None:
            try:
                task.mark_failed(str(e))
                logger.error(f"❌ Task marked as failed: {e}")
            except Exception as e2:
                logger.error(f"Could not mark task as failed: {e2}")
            # Only close if we created the task
            if task_created:
                try:
                    task.close()
                except Exception:
                    pass
        raise


if __name__ == "__main__":
    import sys

    from clearml import Task
    from sklearn.ensemble import (
        AdaBoostClassifier,
        GradientBoostingClassifier,
        RandomForestClassifier,
    )
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.tree import DecisionTreeClassifier

    try:
        # Get parameters from ClearML task if available (when executed by agent)
        task = Task.current_task()
        algorithm_name = "RandomForest"  # default
        params = {}

        if task:
            # Try to get parameters from task
            try:
                task_params = task.get_parameters()
                algorithm_name = task_params.get("algorithm_name", algorithm_name)
                params = task_params.get("params", {})
                logger.info(f"📋 Loaded parameters from ClearML task: {algorithm_name}")
            except Exception as e:
                logger.warning(f"Could not get parameters from task: {e}")

        # Load data
        X_train, X_test, y_train, y_test = load_data()

        # Create model based on algorithm_name
        model_map = {
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
            "KNN": KNeighborsClassifier(n_neighbors=5),
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "GradientBoosting": GradientBoostingClassifier(random_state=42),
            "AdaBoost": AdaBoostClassifier(random_state=42),
            "NaiveBayes": GaussianNB(),
            "MLP": MLPClassifier(random_state=42, max_iter=1000),
        }

        model = model_map.get(
            algorithm_name, RandomForestClassifier(n_estimators=100, random_state=42)
        )

        # Merge params with model defaults (exclude 'algorithm' key)
        if params:
            model_params = {
                k: v for k, v in params.items() if k != "algorithm" and hasattr(model, k)
            }
            if model_params:
                model.set_params(**model_params)
                logger.info(f"✅ Applied parameters: {model_params}")

        # Train model
        accuracy = train_model(algorithm_name, model, X_train, X_test, y_train, y_test, params)

        logger.info(f"✅ Training completed successfully with accuracy: {accuracy:.4f}")

        # Explicitly exit with success code
        sys.exit(0)

    except KeyboardInterrupt:
        logger.error("❌ Training interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"❌ Training failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)  # Exit with error code
