# Code Style Guide

## Форматирование

Проект использует **Black** для автоматического форматирования:

```bash
# Форматировать все файлы
black src tests

# Проверить без изменений
black --check src tests
```

**Настройки:**
- Длина строки: 100 символов
- Python версия: 3.12+

## Линтинг

**Ruff** используется для линтинга:

```bash
# Проверить код
ruff check src tests

# Автоматически исправить
ruff check --fix src tests
```

## Типы

**MyPy** для проверки типов:

```bash
# Проверить типы
mypy src
```

Используйте аннотации типов:

```python
def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_estimators: int = 100,
) -> RandomForestClassifier:
    ...
```

## Документация

Используйте Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    ...
```

## Импорты

Используйте **isort** для сортировки импортов:

```python
# Стандартная библиотека
import json
from pathlib import Path

# Сторонние библиотеки
import numpy as np
import pandas as pd

# Локальные импорты
from src.utils.mlflow_utils import setup_mlflow
```
