# EPML Data Science Project

Проект для курса EPML (Engineering Practices for Machine Learning) - настройка рабочего места Data Scientist.

## 📋 Описание

Этот проект демонстрирует настройку полноценного рабочего места для Data Science с использованием современных инженерных практик:

- ✅ Структура проекта по стандартам Cookiecutter Data Science
- ✅ Управление зависимостями через `uv`
- ✅ Автоматизация через Makefile
- ✅ Контейнеризация с Docker
- ✅ Pre-commit hooks для контроля качества кода
- ✅ Линтеры и форматтеры (Black, isort, Ruff, MyPy, Bandit)
- ✅ Тестирование с pytest
- ✅ Версионирование данных через DVC
- ✅ Версионирование моделей через MLflow

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - быстрый менеджер пакетов Python
- Docker и Docker Compose (опционально)

### Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/EgorovM/itmo_epml
   cd itmo_epml
   ```

2. **Установите зависимости:**
   ```bash
   make setup
   ```
   Или вручную:
   ```bash
   uv pip install -e ".[dev]"
   pre-commit install
   ```

3. **Проверьте установку:**
   ```bash
   make check
   ```

## 📁 Структура проекта

```
epml/
├── src/                    # Исходный код
│   ├── data/              # Загрузка и обработка данных
│   ├── features/          # Инженерия признаков
│   └── models/            # Обучение моделей
├── tests/                 # Тесты
├── notebooks/             # Jupyter ноутбуки
├── data/                  # Данные
│   ├── raw/              # Исходные данные
│   ├── processed/        # Обработанные данные
│   └── external/         # Внешние данные
├── models/                # Сохраненные модели
├── reports/               # Отчеты и визуализации
│   └── figures/          # Графики
├── logs/                  # Логи
├── .dvc/                  # DVC конфигурация и кэш
├── mlruns/                # MLflow tracking данные
├── metrics/               # Метрики экспериментов
├── plots/                 # Данные для графиков
├── params/                # Параметры обучения
├── dvc.yaml              # DVC pipeline
├── pyproject.toml         # Конфигурация проекта и зависимостей
├── .pre-commit-config.yaml # Конфигурация pre-commit hooks
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
└── Makefile              # Автоматизация задач
```

## 🛠️ Использование Makefile

Проект включает Makefile для автоматизации основных задач:

```bash
make help              # Показать все доступные команды
make setup             # Полная настройка проекта
make install           # Установить зависимости
make install-dev       # Установить dev зависимости
make format            # Форматировать код
make lint              # Запустить линтер
make type-check        # Проверить типы
make security-check    # Проверить безопасность
make check             # Запустить все проверки
make test              # Запустить тесты
make test-cov          # Тесты с покрытием
make clean             # Очистить временные файлы
make docker-build      # Собрать Docker образ
make docker-up         # Запустить Docker контейнеры
make run-notebook-docker # Запустить Jupyter в Docker
make dvc-init          # Инициализация DVC
make dvc-repro         # Воспроизведение DVC pipeline
make mlflow-ui         # Запуск MLflow UI
make mlflow-compare    # Сравнение моделей
make train-pipeline    # Полный pipeline (prepare + train)
```

## 🐳 Docker

### Запуск Jupyter Lab в Docker

```bash
make docker-up
# или
docker-compose up -d
```

Jupyter Lab будет доступен по адресу: http://localhost:8888

### Остановка контейнеров

```bash
make docker-down
# или
docker-compose down
```

## 🧪 Тестирование

Запуск тестов:

```bash
make test
```

Запуск тестов с покрытием:

```bash
make test-cov
```

## 🔍 Контроль качества кода

Проект использует следующие инструменты:

- **Black** - форматирование кода
- **isort** - сортировка импортов
- **Ruff** - быстрый линтер
- **MyPy** - проверка типов
- **Bandit** - проверка безопасности
- **Pre-commit** - автоматические проверки перед коммитом

Запуск всех проверок:

```bash
make check
```

## 📦 Управление зависимостями

Проект использует `uv` для управления зависимостями. Все зависимости определены в `pyproject.toml`.

### Добавление новой зависимости

```bash
uv pip install package-name
```

### Генерация requirements.txt

```bash
make requirements
```

## 🔧 Настройка Git

Проект включает `.gitignore` для ML проектов, который исключает:
- Python кэш файлы
- Виртуальные окружения
- Данные и модели
- Jupyter notebook outputs
- Логи и отчеты

## 🌿 Git Workflow

### Стратегия ветвления

Проект использует Git Flow для организации работы:

```
main          # Основная ветка (production-ready код)
├── develop   # Ветка разработки (интеграция функций)
├── feature/* # Ветки для новых функций
├── bugfix/*  # Ветки для исправления багов
└── experiment/* # Ветки для экспериментов с моделями
```

### Описание веток

- **main** - стабильная версия проекта, готовая к демонстрации
- **develop** - ветка для интеграции новых функций перед релизом
- **feature/*** - разработка новых функций (например, `feature/new-model`)
- **bugfix/*** - исправление ошибок (например, `bugfix/fix-data-loading`)
- **experiment/*** - эксперименты с моделями и данными (например, `experiment/iris-svm`)

### Workflow

1. **Создание feature ветки:**
   ```bash
   git checkout develop
   git checkout -b feature/new-feature
   ```

2. **Разработка и коммиты:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Слияние в develop:**
   ```bash
   git checkout develop
   git merge feature/new-feature
   ```

4. **Релиз в main:**
   ```bash
   git checkout main
   git merge develop
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```

## 📊 Версионирование данных и моделей

Проект использует **DVC** для версионирования данных и **MLflow** для версионирования моделей.

### DVC - Версионирование данных

#### Установка и инициализация

```bash
# DVC уже установлен через зависимости
dvc init --no-scm
```

#### Настройка remote storage

**Local storage (по умолчанию):**
```bash
dvc remote add -d local .dvc/cache
```

**S3 storage (опционально):**
```bash
dvc remote add s3 s3://epml-data/models
dvc remote modify s3 endpointurl <your-endpoint>
```

#### Добавление данных в DVC

```bash
# Скачать данные
python src/data/download_data.py

# Добавить в DVC
dvc add data/raw/iris.csv

# Закоммитить .dvc файл
git add data/raw/iris.csv.dvc .gitignore
git commit -m "Add iris dataset to DVC"
```

#### Воспроизведение pipeline

```bash
# Запустить весь pipeline
dvc repro

# Или отдельные этапы
dvc repro prepare_data
dvc repro train
```

#### Работа с версиями

```bash
# Просмотр истории
dvc list data/raw/

# Откат к предыдущей версии
git checkout HEAD~1 data/raw/iris.csv.dvc
dvc checkout
```

### MLflow - Версионирование моделей

#### Запуск MLflow UI

```bash
# Локально
mlflow ui --host 0.0.0.0 --port 5000

# Или через Makefile
make mlflow-ui

# В Docker
docker-compose up mlflow
# Доступен на http://localhost:5001
```

#### Обучение модели с MLflow

```bash
# Подготовить данные
python src/data/prepare_data.py

# Обучить модель
python src/models/train_with_mlflow.py
```

#### Сравнение моделей

```bash
python src/models/compare_models.py
```

#### Просмотр метаданных

MLflow автоматически сохраняет:
- Параметры модели (из `params/training.yaml`)
- Метрики (accuracy, n_samples, n_features)
- Артефакты (модель, метрики в JSON)
- Версию кода и окружения

### Полный pipeline

```bash
# 1. Подготовить данные
python src/data/download_data.py
dvc add data/raw/iris.csv

# 2. Запустить pipeline
dvc repro

# 3. Просмотреть результаты в MLflow
make mlflow-ui
```

### Воспроизводимость

Все зависимости зафиксированы в `pyproject.toml`. Для воспроизведения:

```bash
# 1. Установить зависимости
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. Восстановить данные
dvc pull

# 3. Воспроизвести pipeline
dvc repro
```
