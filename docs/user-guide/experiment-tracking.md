# Трекинг экспериментов

## MLflow

### Запуск экспериментов

```bash
# Запустить все эксперименты
make run-experiments

# Сравнить результаты
make compare-experiments
```

### Использование в коде

```python
from src.utils.mlflow_utils import setup_mlflow, track_experiment

# Настроить MLflow
setup_mlflow()

# Использовать декоратор
@track_experiment()
def train_model(X_train, y_train):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return {"accuracy": model.score(X_test, y_test)}
```

## ClearML

### Запуск экспериментов

```bash
# Запустить ClearML Server
make clearml-up

# Запустить эксперименты
make clearml-experiments
```

### Использование в коде

```python
from src.clearml_utils.setup import setup_clearml
from src.clearml_utils.tracking import log_parameters, log_metrics

task = setup_clearml(project_name="EPML", task_name="experiment")
log_parameters({"n_estimators": 100}, task)
log_metrics({"accuracy": 0.95}, task=task)
```
