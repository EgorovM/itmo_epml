"""Demo script to run all ClearML features."""

import logging

from clearml import PipelineController

from src.clearml_utils.model_registry import compare_models, get_model_versions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_pipeline():
    """Create and run a demo pipeline."""
    logger.info("🔧 Creating pipeline...")

    # Create pipeline
    pipeline = PipelineController(
        name="iris_training_pipeline",
        project="EPML",
        version="1.0.0",
    )

    # Add steps (these are placeholder - actual tasks should exist)
    pipeline.add_step(
        name="prepare_data",
        base_task_project="EPML",
        base_task_name="prepare_data",
    )

    pipeline.add_step(
        name="train_model",
        base_task_project="EPML",
        base_task_name="train_model",
        parents=["prepare_data"],
    )

    logger.info(f"✅ Pipeline created: {pipeline.id}")
    return pipeline


def demo_model_registry():
    """Demonstrate model registry features."""
    logger.info("📦 Checking model registry...")

    # Get all models
    models = get_model_versions("RandomForest_iris", project_name="EPML")
    logger.info(f"Found {len(models)} versions of RandomForest_iris")

    # Compare models
    if models:
        comparisons = compare_models("RandomForest_iris", project_name="EPML", metric="accuracy")
        logger.info(f"✅ Model comparison: {len(comparisons)} versions compared")
        for comp in comparisons[:3]:
            logger.info(f"  - Version {comp['version']}: accuracy={comp.get('metric', 'N/A')}")

    return models


def main():
    """Run all demos."""
    logger.info("=" * 80)
    logger.info("🎬 ClearML Demo Script")
    logger.info("=" * 80)

    # 1. Pipeline
    try:
        pipeline = demo_pipeline()
        logger.info(f"✅ Pipeline ID: {pipeline.id}")
    except Exception as e:
        logger.warning(f"⚠️ Pipeline demo failed: {e}")

    # 2. Model Registry
    try:
        models = demo_model_registry()
        logger.info(f"✅ Model registry: {len(models)} models found")
    except Exception as e:
        logger.warning(f"⚠️ Model registry demo failed: {e}")

    logger.info("=" * 80)
    logger.info("✅ Demo completed! Check ClearML UI at http://localhost:8080")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
