# Структура проекта

## Обзор

```
epml/
├── src/                      # Исходный код
│   ├── data/                 # Скрипты для работы с данными
│   ├── models/               # Модели и обучение
│   ├── experiments/          # Эксперименты
│   ├── pipeline/             # Пайплайны
│   ├── utils/                # Утилиты
│   └── clearml_utils/        # ClearML утилиты
├── docs/                     # Документация MkDocs
├── reports/                  # Отчеты об экспериментах
├── conf/                     # Конфигурации Hydra
│   ├── config.yaml
│   ├── model/
│   └── data/
├── data/                     # Данные (версионируются через DVC)
│   ├── raw/                  # Исходные данные
│   └── processed/            # Обработанные данные
├── models/                   # Сохраненные модели
├── metrics/                  # Метрики экспериментов
├── plots/                    # Графики и визуализации
├── logs/                     # Логи выполнения
├── .dvc/                     # DVC метаданные
├── mlruns/                   # MLflow данные (игнорируется в Git)
├── dvc.yaml                  # DVC pipeline
├── params.yaml               # Параметры для DVC
├── pyproject.toml            # Зависимости и конфигурация
├── mkdocs.yml                # Конфигурация MkDocs
├── Dockerfile                # Docker образ
├── docker-compose.yml        # Docker Compose для разработки
├── docker-compose.clearml.yml # Docker Compose для ClearML
├── Makefile                  # Автоматизация задач
└── README.md                 # Основной README
```

## Описание директорий

### `src/`

Исходный код проекта, организованный по модулям:

- **`data/`** - загрузка и подготовка данных
- **`models/`** - обучение и оценка моделей
- **`experiments/`** - скрипты для экспериментов
- **`pipeline/`** - пайплайны с Hydra
- **`utils/`** - утилиты (MLflow, общие функции)
- **`clearml_utils/`** - утилиты для ClearML

### `docs/`

Документация проекта в формате Markdown для MkDocs.

### `reports/`

Отчеты об экспериментах в формате Markdown:
- `HW1_REPORT.md` - Настройка рабочего места
- `HW2_REPORT.md` - Версионирование данных и моделей
- `HW3_REPORT.md` - Трекинг экспериментов
- `HW4_REPORT.md` - Автоматизация пайплайнов
- `HW5_REPORT.md` - ClearML для MLOps

### `conf/`

Конфигурации Hydra для управления параметрами:
- `config.yaml` - основная конфигурация
- `model/` - конфигурации моделей
- `data/` - конфигурации данных

### `data/`

Данные проекта, версионируемые через DVC:
- `raw/` - исходные данные
- `processed/` - обработанные данные

### `models/`

Сохраненные обученные модели.

### `metrics/`

Метрики экспериментов в формате JSON.

### `plots/`

Графики и визуализации результатов.

## Ключевые файлы

### `dvc.yaml`

Определяет DVC pipeline с этапами:
- `prepare_data` - подготовка данных
- `train_*` - обучение различных моделей
- `compare_models` - сравнение моделей

### `params.yaml`

Параметры для DVC pipeline.

### `pyproject.toml`

Конфигурация проекта:
- Зависимости
- Настройки инструментов (Black, Ruff, MyPy)
- Метаданные проекта

### `Makefile`

Автоматизация задач:
- `make setup` - установка
- `make test` - тесты
- `make lint` - проверка кода
- `make run-experiments` - запуск экспериментов
