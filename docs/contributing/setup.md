# Development Setup

## Настройка окружения разработки

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/epml.git
cd epml
```

### 2. Создать виртуальное окружение

```bash
uv venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
uv pip install -e ".[dev]"
```

### 4. Настроить pre-commit

```bash
pre-commit install
```

### 5. Инициализировать DVC

```bash
dvc init
```

## Структура разработки

### Создание нового модуля

1. Создайте файл в соответствующей директории `src/`
2. Добавьте тесты в `tests/`
3. Обновите документацию в `docs/`

### Стиль кода

Проект использует:
- **Black** для форматирования
- **Ruff** для линтинга
- **MyPy** для проверки типов

```bash
# Форматировать код
make format

# Проверить код
make lint

# Проверить типы
make type-check
```

## Тестирование

```bash
# Запустить все тесты
make test

# Запустить конкретный тест
pytest tests/test_models.py

# С покрытием
pytest --cov=src tests/
```

## Коммиты

Используйте осмысленные сообщения коммитов:

```
feat: add new model training script
fix: correct data loading issue
docs: update installation guide
```
