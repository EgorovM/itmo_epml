# Пайплайны

## DVC Pipelines

### Структура pipeline

Pipeline определен в `dvc.yaml`:

```yaml
stages:
  prepare_data:
    cmd: python src/data/prepare_data.py
    deps:
      - src/data/prepare_data.py
    outs:
      - data/processed/iris_processed.csv
```

### Запуск pipeline

```bash
# Воспроизвести весь pipeline
dvc repro

# Воспроизвести конкретный этап
dvc repro train_random_forest

# Просмотреть граф
dvc dag
```

## Hydra конфигурации

### Использование конфигураций

```bash
# Обучить с конкретной моделью
python src/pipeline/train_with_config.py model=random_forest

# Переопределить параметры
python src/pipeline/train_with_config.py model=svm model.C=10.0
```

### Создание новых конфигураций

1. Создайте файл в `conf/model/`
2. Определите параметры модели
3. Используйте через CLI
