# Развертывание с Docker

## Docker Compose

Проект включает несколько Docker Compose конфигураций:

### Основной Docker Compose

`docker-compose.yml` - для разработки:

```bash
# Запустить Jupyter Lab и MLflow
docker-compose up -d

# Просмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

**Сервисы:**
- Jupyter Lab: http://localhost:8888
- MLflow UI: http://localhost:5001

### ClearML Docker Compose

`docker-compose.clearml.yml` - для ClearML Server:

```bash
# Запустить ClearML Server
make clearml-up

# Проверить статус
make clearml-status

# Остановить
make clearml-down
```

**Сервисы:**
- API Server: http://localhost:8008
- Web Server: http://localhost:8080
- Files Server: http://localhost:8081

## Dockerfile

Основной Dockerfile для проекта:

```dockerfile
FROM python:3.12-slim

# Установка зависимостей
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system -e ".[dev]"

WORKDIR /app
COPY . .

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888"]
```

## Сборка образа

```bash
# Собрать образ
docker build -t epml:latest .

# Запустить контейнер
docker run -p 8888:8888 epml:latest
```

## Переменные окружения

Создайте файл `.env` для переменных окружения:

```bash
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
CLEARML_API_ACCESS_KEY=your_key
CLEARML_API_SECRET_KEY=your_secret
```

Используйте в docker-compose:

```yaml
services:
  app:
    env_file:
      - .env
```
