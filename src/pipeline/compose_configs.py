"""Utilities for composing configurations."""

from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig


def get_config(
    base_config: str = "config",
    model: str | None = None,
    data: str | None = None,
    overrides: list[str] | None = None,
) -> DictConfig:
    """Compose configuration from multiple sources.

    Args:
        base_config: Base configuration name
        model: Model configuration name
        data: Data configuration name
        overrides: Additional configuration overrides

    Returns:
        Composed configuration
    """
    config_dir = Path(__file__).parent.parent.parent / "conf"
    overrides_list = overrides or []

    if model:
        overrides_list.append(f"model={model}")
    if data:
        overrides_list.append(f"data={data}")

    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        cfg = compose(config_name=base_config, overrides=overrides_list)
        return cfg


def list_available_configs(config_type: str = "model") -> list[str]:
    """List available configuration files.

    Args:
        config_type: Type of configuration (model, data)

    Returns:
        List of available configuration names
    """
    config_dir = Path(__file__).parent.parent.parent / "conf" / config_type
    if not config_dir.exists():
        return []

    configs = []
    for config_file in config_dir.glob("*.yaml"):
        configs.append(config_file.stem)

    return sorted(configs)


if __name__ == "__main__":
    # Example usage
    print("Available models:", list_available_configs("model"))
    print("Available datasets:", list_available_configs("data"))

    # Compose config
    cfg = get_config(model="random_forest")
    print("\nComposed config:")
    from omegaconf import OmegaConf

    print(OmegaConf.to_yaml(cfg))
