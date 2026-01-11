# Версионирование данных

## DVC для версионирования данных

Проект использует DVC (Data Version Control) для управления версиями данных.

### Инициализация

```bash
# Инициализировать DVC
dvc init

# Настроить remote storage
dvc remote add -d local .dvc/cache
```

### Добавление данных

```bash
# Добавить файл в DVC
dvc add data/raw/iris.csv

# Закоммитить .dvc файл
git add data/raw/iris.csv.dvc .gitignore
git commit -m "Add iris dataset"
```

### Воспроизведение

```bash
# Воспроизвести pipeline
dvc repro

# Получить данные из remote
dvc pull
```

## Структура данных

```
data/
├── raw/           # Исходные данные (версионируются)
└── processed/     # Обработанные данные (версионируются)
```
