# Версионирование моделей

## MLflow для версионирования моделей

Проект использует MLflow для управления версиями моделей.

### Обучение с MLflow

```bash
# Обучить модель
python src/models/train_with_mlflow.py

# Или через Makefile
make train-pipeline
```

### Просмотр моделей

```bash
# Запустить MLflow UI
make mlflow-ui-db

# Открыть http://localhost:5000
```

### Сравнение моделей

```bash
# Сравнить модели
make compare-experiments
```

## ClearML для версионирования моделей

ClearML также поддерживает версионирование моделей.

```bash
# Запустить ClearML Server
make clearml-up

# Обучить модель
make clearml-train
```
