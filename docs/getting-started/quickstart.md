# Быстрый старт

Это руководство поможет вам быстро начать работу с проектом EPML.

## Подготовка данных

```bash
# Подготовить данные
python src/data/prepare_data.py
```

## Запуск экспериментов

### С MLflow

```bash
# Запустить все эксперименты
make run-experiments

# Сравнить результаты
make compare-experiments

# Открыть MLflow UI
make mlflow-ui-db
# Откройте http://localhost:5000
```

### С ClearML

```bash
# Запустить ClearML Server
make clearml-up

# Запустить эксперименты
make clearml-experiments

# Открыть ClearML UI
# Откройте http://localhost:8080
# Логин: admin, Пароль: admin
```

## Обучение модели с конфигурацией

```bash
# Обучить модель с Hydra конфигурацией
make pipeline-train MODEL=random_forest

# Или напрямую
python src/pipeline/train_with_config.py model=random_forest
```

## Запуск DVC Pipeline

```bash
# Воспроизвести весь pipeline
dvc repro

# Воспроизвести конкретный этап
dvc repro train_random_forest

# Просмотреть граф зависимостей
dvc dag
```

## Примеры использования

### Базовый пример обучения модели

```python
from src.utils.mlflow_utils import setup_mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

# Настроить MLflow
setup_mlflow()

# Загрузить данные
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# Обучить модель
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Оценить
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")
```

### Использование декоратора для трекинга

```python
from src.utils.mlflow_utils import track_experiment

@track_experiment()
def train_model(X_train, y_train):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return {"accuracy": model.score(X_test, y_test)}
```

### Использование контекстного менеджера

```python
from src.utils.mlflow_utils import mlflow_run

with mlflow_run(run_name="my_experiment", tags={"algorithm": "RF"}):
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
```

## Следующие шаги

- Изучите [Структуру проекта](../user-guide/structure.md)
- Прочитайте [Руководство по версионированию](../user-guide/data-versioning.md)
- Посмотрите [Примеры экспериментов](../reports/experiments.md)
