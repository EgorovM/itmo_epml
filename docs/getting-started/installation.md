# Установка

## Требования

- Python 3.12+
- Docker и Docker Compose (для контейнеризации)
- Git
- `uv` (менеджер пакетов)

## Установка зависимостей

### Использование uv (рекомендуется)

```bash
# Создать виртуальное окружение
uv venv

# Активировать окружение
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows

# Установить зависимости
uv pip install -e ".[dev]"
```

### Использование pip

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -e ".[dev]"
```

## Проверка установки

```bash
# Проверить версию Python
python --version  # Должно быть 3.12+

# Проверить установленные пакеты
pip list | grep -E "(dvc|mlflow|clearml|hydra)"

# Запустить тесты
make test
```

## Установка дополнительных инструментов

### DVC

DVC устанавливается автоматически через зависимости. Для настройки:

```bash
# Инициализировать DVC
dvc init

# Настроить remote storage (опционально)
dvc remote add -d local .dvc/cache
```

### MLflow

MLflow устанавливается автоматически. Для запуска UI:

```bash
# Запустить MLflow UI
make mlflow-ui-db
```

### ClearML

ClearML устанавливается автоматически. Для запуска сервера:

```bash
# Запустить ClearML Server через Docker
make clearml-up
```

## Docker установка

```bash
# Собрать образ
docker-compose build

# Запустить сервисы
docker-compose up -d
```

## Следующие шаги

После установки перейдите к [Быстрому старту](quickstart.md).
