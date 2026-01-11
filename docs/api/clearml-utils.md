# ClearML Utils API

## Модуль: `src.clearml_utils`

Утилиты для работы с ClearML.

## Модули

### `setup`

Настройка ClearML.

```python
from src.clearml_utils.setup import setup_clearml

task = setup_clearml(
    project_name="EPML",
    task_name="experiment_name",
    tags=["iris", "classification"],
)
```

### `tracking`

Трекинг экспериментов.

```python
from src.clearml_utils.tracking import log_parameters, log_metrics

log_parameters({"n_estimators": 100}, task)
log_metrics({"accuracy": 0.95}, task=task)
```

### `model_registry`

Управление моделями.

```python
from src.clearml_utils.model_registry import register_model

model = register_model(
    model_path="models/model.pkl",
    model_name="iris_classifier",
    project_name="EPML",
)
```

### `pipeline`

Пайплайны ClearML.

```python
from src.clearml_utils.pipeline import create_training_pipeline

pipeline = create_training_pipeline(
    pipeline_name="iris_training",
    project_name="EPML",
)
```
