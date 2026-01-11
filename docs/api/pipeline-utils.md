# Pipeline Utils API

## Модуль: `src.pipeline`

Утилиты для работы с пайплайнами.

## Функции

### `train_with_config`

Обучение модели с Hydra конфигурацией.

```python
from src.pipeline.train_with_config import train

# Используется через Hydra CLI
# python src/pipeline/train_with_config.py model=random_forest
```

### `validate_config`

Валидация конфигурации.

```python
from src.pipeline.validate_config import validate_config, compose_configs

cfg = compose_configs(model="random_forest")
result = validate_config(cfg)
print(result["valid"])
```

### `monitor`

Мониторинг выполнения пайплайна.

```python
from src.pipeline.monitor import PipelineMonitor

monitor = PipelineMonitor()
monitor.log_stage_start("prepare_data")
monitor.log_stage_complete("prepare_data", duration=10.5)
```
