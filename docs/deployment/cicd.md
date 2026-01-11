# CI/CD

## GitHub Actions

Проект использует GitHub Actions для автоматизации:

### Документация

`.github/workflows/docs.yml` - автоматическая публикация документации:

- Триггер: push в `main` с изменениями в `docs/`
- Действия:
  - Установка зависимостей
  - Сборка MkDocs
  - Публикация на GitHub Pages

### Тестирование

Пример workflow для тестирования:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: make test
      - run: make lint
```

## Локальная проверка

Перед коммитом:

```bash
# Запустить тесты
make test

# Проверить код
make lint

# Проверить типы
make type-check

# Проверить документацию
mkdocs build
```

## Автоматизация

Используйте pre-commit hooks:

```bash
# Установить hooks
pre-commit install

# Запустить вручную
pre-commit run --all-files
```
