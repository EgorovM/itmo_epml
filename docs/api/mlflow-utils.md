# MLflow Utils API

## Модуль: `src.utils.mlflow_utils`

Утилиты для работы с MLflow.

## Функции

### `setup_mlflow`

Настройка MLflow tracking.

```python
from src.utils.mlflow_utils import setup_mlflow

setup_mlflow(
    tracking_uri="sqlite:///mlflow.db",
    experiment_name="iris-classification",
    reset_db=False,
)
```

**Параметры:**
- `tracking_uri` (str): URI для MLflow tracking
- `experiment_name` (str): Имя эксперимента
- `reset_db` (bool): Сбросить базу данных при ошибках миграции

### `track_experiment`

Декоратор для автоматического трекинга экспериментов.

```python
from src.utils.mlflow_utils import track_experiment

@track_experiment()
def train_model(X_train, y_train):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return {"accuracy": model.score(X_test, y_test)}
```

### `mlflow_run`

Контекстный менеджер для MLflow runs.

```python
from src.utils.mlflow_utils import mlflow_run

with mlflow_run(run_name="my_experiment", tags={"algorithm": "RF"}):
    model.fit(X_train, y_train)
    mlflow.log_metric("accuracy", accuracy)
```

### `compare_experiments`

Сравнение экспериментов.

```python
from src.utils.mlflow_utils import compare_experiments

compare_experiments(
    experiment_name="iris-classification",
    tracking_uri="sqlite:///mlflow.db",
    metric="accuracy",
    top_n=5,
)
```
