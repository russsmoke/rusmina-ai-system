# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```
Новые параметры для команды report:
- `--max-hist-columns` - Ограничивает количество числовых колонок для построения гистограмм (по умолчанию `6`).
```bash
uv run eda-cli report data/example.csv --max-hist-columns 10
```
- `--top-k-categories` - Определяет, сколько топ-значений выводить для категориальных признаков (по умолчанию `5`).
```bash
uv run eda-cli report data/example.csv --top-k-categories 3
```
- `--title` - Задаёт заголовок Markdown отчёта (по умолчанию: `"EDA-отчёт"`).
```bash
uv run eda-cli report data/example.csv --title "Анализ данных пользователей"
```
- `--min-missing-share` - Порог доли пропусков (от 0.0 до 1.0), выше которого колонка считается проблемной. Такие колонки попадают в отдельный раздел отчёта (по умолчанию: `0.3`).
```bash
uv run eda-cli report data/example.csv --min-missing-share 0.1
```
#### Пример вызова с новыми опциями
```bash 
    uv run eda-cli report data/example.csv --out-dir "reports" --max-hist-columns 8 --top-k-categories 5 --title "Анализ продаж" --min-missing-share 0.2    
```
В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

### Новые эвристики качества
В отчёте теперь отображаются дополнительные метрики качества:
- Наличие константных колонок
- Категориальные признаки с высокой кардинальностью (>20 уникальных значений)

## Тесты

```bash
uv run pytest -q
```
