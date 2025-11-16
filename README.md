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
