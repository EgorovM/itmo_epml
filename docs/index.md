# EPML Project Documentation

Добро пожаловать в документацию проекта **EPML** (Engineering Practices for Machine Learning)!

Этот проект демонстрирует современные практики разработки ML-проектов, включая:

- 🔧 **Настройка рабочего места Data Scientist**
- 📊 **Версионирование данных и моделей** (DVC, MLflow)
- 🧪 **Трекинг экспериментов** (MLflow, ClearML)
- 🔄 **Автоматизация ML пайплайнов** (DVC Pipelines, Hydra)
- 🚀 **MLOps с ClearML**
- 📚 **Документация и отчеты**

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/epml.git
cd epml

# Установить зависимости
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Запустить эксперименты
make run-experiments
```

## Основные возможности

### Версионирование данных и моделей

- **DVC** для версионирования данных
- **MLflow** для версионирования моделей
- Автоматическое создание версий при изменениях

### Трекинг экспериментов

- Автоматическое логирование метрик и параметров
- Сравнение экспериментов
- Визуализация результатов

### Автоматизация пайплайнов

- **DVC Pipelines** для оркестрации
- **Hydra** для управления конфигурациями
- Параллельное выполнение этапов

### MLOps

- **ClearML** для комплексного MLOps workflow
- Управление моделями
- Пайплайны и мониторинг

## Структура проекта

```
epml/
├── src/              # Исходный код
├── docs/             # Документация
├── reports/          # Отчеты об экспериментах
├── conf/             # Конфигурации Hydra
├── data/             # Данные (версионируются через DVC)
├── models/           # Модели
├── metrics/          # Метрики
└── mkdocs.yml        # Конфигурация MkDocs
```

## Документация

- [Установка](getting-started/installation.md)
- [Быстрый старт](getting-started/quickstart.md)
- [Руководство пользователя](user-guide/structure.md)
- [Развертывание](deployment/docker.md)
- [API Reference](api/mlflow-utils.md)

## Отчеты

- [Отчеты об экспериментах](reports/experiments.md)
- [Сравнение моделей](reports/comparison.md)

## Лицензия

Проект распространяется под лицензией MIT.
