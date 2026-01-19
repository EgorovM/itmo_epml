"""Script to train model with MLflow tracking."""

import json
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from src.utils.mlflow_utils import mlflow_run, setup_mlflow


def load_params():
    """Load training parameters from params.yaml."""
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    return params["train"]


def train_model():
    """Train Random Forest classifier and log to MLflow."""
    # Load parameters
    train_params = load_params()

    # Load processed data
    data_path = Path("data/processed/iris_processed.csv")
    if not data_path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {data_path}. "
            "Please run 'python src/data/prepare_data.py' first."
        )

    df = pd.read_csv(data_path)
    X = df.drop(columns=["target", "target_name"])
    y = df["target"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=train_params["test_size"],
        random_state=train_params["random_state"],
    )

    setup_mlflow(tracking_uri="sqlite:///mlflow.db", experiment_name="iris_classification")

    with mlflow_run(run_name="train_random_forest"):
        # Log parameters
        mlflow.log_params(train_params)

        # Train model
        model = RandomForestClassifier(
            n_estimators=train_params["n_estimators"],
            max_depth=train_params["max_depth"],
            min_samples_split=train_params["min_samples_split"],
            random_state=train_params["random_state"],
        )
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Generate classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        mlflow.log_dict(report, "classification_report.json")

        print("✅ Model trained successfully!")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   MLflow run ID: {mlflow.active_run().info.run_id}")

        # Save metrics
        metrics_dir = Path("metrics")
        metrics_dir.mkdir(exist_ok=True)
        metrics = {
            "accuracy": float(accuracy),
            "n_samples": len(X_test),
            "n_features": X_test.shape[1],
        }
        metrics_file = metrics_dir / "model_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"✅ Metrics saved to {metrics_file}")

        # Save model
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        model_path = models_dir / "iris_classifier.pkl"
        joblib.dump(model, model_path)
        print(f"✅ Model saved to {model_path}")

    return model, accuracy


if __name__ == "__main__":
    train_model()
