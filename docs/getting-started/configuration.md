# Конфигурация

Проект использует несколько систем конфигурации для разных целей.

## Hydra конфигурации

Конфигурации Hydra находятся в директории `conf/`:

```
conf/
├── config.yaml              # Основная конфигурация
├── model/                    # Конфигурации моделей
│   ├── random_forest.yaml
│   ├── svm.yaml
│   └── ...
└── data/                     # Конфигурации данных
    └── iris.yaml
```

### Основная конфигурация

`conf/config.yaml` содержит общие настройки:

```yaml
project:
  name: epml
  version: 0.1.0

paths:
  data_raw: data/raw
  data_processed: data/processed
  models: models
  metrics: metrics

mlflow:
  tracking_uri: sqlite:///mlflow.db
  experiment_name: iris-classification

train:
  test_size: 0.2
  random_state: 42
```

### Конфигурации моделей

Пример конфигурации модели (`conf/model/random_forest.yaml`):

```yaml
_target_: sklearn.ensemble.RandomForestClassifier
n_estimators: 100
max_depth: null
min_samples_split: 2
random_state: 42
algorithm: RandomForest
```

### Использование конфигураций

```bash
# Использовать конкретную модель
python src/pipeline/train_with_config.py model=random_forest

# Переопределить параметры
python src/pipeline/train_with_config.py model=svm model.C=10.0
```

## DVC конфигурация

DVC использует файл `params.yaml` для параметров pipeline:

```yaml
train:
  test_size: 0.2
  random_state: 42
  n_estimators: 100
```

## MLflow конфигурация

MLflow настраивается через переменные окружения или код:

```python
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("iris-classification")
```

## ClearML конфигурация

ClearML настраивается через переменные окружения:

```bash
export CLEARML_API_ACCESS_KEY="your_key"
export CLEARML_API_SECRET_KEY="your_secret"
```

Или через файл `~/.clearml/clearml.conf`.

## Переменные окружения

Создайте файл `.env` для локальной разработки:

```bash
# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# ClearML
CLEARML_API_ACCESS_KEY=your_key
CLEARML_API_SECRET_KEY=your_secret

# Python
PYTHONPATH=.
```
