"""Training script with Hydra configuration."""

import json
import logging
from pathlib import Path
from typing import Any, cast

import hydra
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from omegaconf import DictConfig, OmegaConf
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from src.utils.mlflow_utils import setup_mlflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_data(cfg: DictConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Load and prepare data based on configuration."""
    data_file = Path(cfg.paths.data_processed) / "iris_processed.csv"
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

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=cfg.train.test_size,
        random_state=cfg.train.random_state,
    )
    return X_train, X_test, y_train, y_test


def instantiate_model(cfg: DictConfig):
    """Instantiate model from configuration using Hydra's instantiate."""
    from hydra.utils import instantiate

    model_cfg = cast(dict[str, Any], OmegaConf.to_container(cfg.model, resolve=True))
    # Get algorithm before instantiation
    algorithm = model_cfg.get("algorithm", "unknown")
    # Remove algorithm from config before instantiation (it's not a model parameter)
    model_params = {k: v for k, v in model_cfg.items() if k != "algorithm"}
    model = instantiate(model_params)
    return model, algorithm


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def train(cfg: DictConfig) -> None:
    """Train model with Hydra configuration."""
    logger.info("🚀 Starting training pipeline")
    logger.info(f"Configuration:\n{OmegaConf.to_yaml(cfg)}")

    # Setup MLflow
    setup_mlflow(
        tracking_uri=cfg.mlflow.tracking_uri,
        experiment_name=cfg.mlflow.experiment_name,
    )

    # Load data
    X_train, X_test, y_train, y_test = load_data(cfg)

    # Instantiate model
    model, algorithm = instantiate_model(cfg)

    # Start MLflow run
    with mlflow.start_run(run_name=f"{algorithm}_{cfg.train.random_state}"):
        # Log configuration
        train_params = cast(dict[str, Any], OmegaConf.to_container(cfg.train, resolve=True))
        model_params = cast(dict[str, Any], OmegaConf.to_container(cfg.model, resolve=True))
        mlflow.log_params(train_params)
        mlflow.log_params(model_params)
        mlflow.set_tag("algorithm", algorithm)
        mlflow.log_param("algorithm", algorithm)

        # Train model
        logger.info(f"Training {algorithm}...")
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("train_accuracy", model.score(X_train, y_train))
        mlflow.log_metric("n_samples", len(X_train))
        mlflow.log_metric("n_features", X_train.shape[1])

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Save model locally
        models_dir = Path(cfg.paths.models)
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / f"{algorithm.lower()}_model.pkl"
        joblib.dump(model, model_path)
        mlflow.log_artifact(str(model_path), "models")

        # Save metrics
        metrics_dir = Path(cfg.paths.metrics)
        metrics_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "accuracy": float(accuracy),
            "algorithm": algorithm,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }
        metrics_file = metrics_dir / f"{algorithm.lower()}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        mlflow.log_artifact(str(metrics_file), "metrics")

        logger.info(f"✅ Model trained with accuracy: {accuracy:.4f}")
        logger.info(f"✅ Model saved to {model_path}")
        logger.info(f"✅ Metrics saved to {metrics_file}")


if __name__ == "__main__":
    train()
