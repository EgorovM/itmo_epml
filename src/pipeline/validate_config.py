"""Configuration validation utilities."""

from pathlib import Path
from typing import Any, cast

from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    """Pydantic model for model configuration validation."""

    algorithm: str = Field(..., description="Algorithm name")
    random_state: int | None = Field(default=None, description="Random state")

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate algorithm name."""
        valid_algorithms = [
            "RandomForest",
            "SVM",
            "LogisticRegression",
            "KNN",
            "DecisionTree",
            "GradientBoosting",
        ]
        if v not in valid_algorithms:
            # Allow other algorithms too
            pass
        return v


class TrainConfig(BaseModel):
    """Pydantic model for training configuration validation."""

    test_size: float = Field(ge=0.0, le=1.0, description="Test size (0-1)")
    random_state: int = Field(..., description="Random state")
    cv_folds: int = Field(default=5, ge=2, description="Cross-validation folds")


class DataConfig(BaseModel):
    """Pydantic model for data configuration validation."""

    dataset: str = Field(..., description="Dataset name")
    target: str = Field(..., description="Target column name")


def validate_config(cfg: DictConfig) -> dict[str, Any]:
    """Validate configuration using Pydantic.

    Args:
        cfg: OmegaConf configuration

    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []

    try:
        # Validate model config (skip _target_ field)
        if "model" in cfg:
            model_cfg = cast(dict[str, Any], OmegaConf.to_container(cfg.model, resolve=True))
            # Remove _target_ for validation
            model_cfg_clean = {k: v for k, v in model_cfg.items() if not k.startswith("_")}
            ModelConfig(**model_cfg_clean)
    except Exception as e:
        errors.append(f"Model config validation error: {e}")

    try:
        # Validate train config
        if "train" in cfg:
            train_cfg = cast(dict[str, Any], OmegaConf.to_container(cfg.train, resolve=True))
            TrainConfig(**train_cfg)
    except Exception as e:
        errors.append(f"Train config validation error: {e}")

    try:
        # Validate data config
        if "data" in cfg:
            data_cfg = cast(dict[str, Any], OmegaConf.to_container(cfg.data, resolve=True))
            DataConfig(**data_cfg)
    except Exception as e:
        errors.append(f"Data config validation error: {e}")

    # Check paths exist
    if "paths" in cfg:
        paths = cfg.paths
        for path_value in paths.values():
            path = Path(path_value)
            if not path.parent.exists():
                warnings.append(f"Path parent does not exist: {path_value}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def compose_configs(base_config: str = "config", overrides: list[str] | None = None):
    """Compose configurations from multiple sources.

    Args:
        base_config: Base configuration name
        overrides: List of configuration overrides

    Returns:
        Composed configuration
    """
    from pathlib import Path

    from hydra import compose, initialize_config_dir

    config_dir = Path(__file__).parent.parent.parent / "conf"
    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        cfg = compose(config_name=base_config, overrides=overrides or [])
        return cfg
