# PetCare backend

API на FastAPI: питомцы, карта здоровья, журнал питания, замеры, напоминания с Web Push, фото и аватары в RustFS, PDF-отчёт.

Полная техническая спецификация (требования, архитектурные решения, C4, модель данных, эндпоинты, тесты, CI/CD) — [`docs/spec.md`](docs/spec.md).

## Документы

| Файл | Что это |
|---|---|
| [`docs/spec.md`](docs/spec.md) | Техническая спецификация |
| [`docs/presentation.pdf`](docs/presentation.pdf) | Презентация |
| [`docs/openapi.json`](docs/openapi.json) | Контракт API; Swagger UI — `/docs` на запущенном сервисе |
| [`docs/db-schema.png`](docs/db-schema.png) | Схема БД |
| [`docs/petcare.postman_collection.json`](docs/petcare.postman_collection.json) | Коллекция Postman |

## Стек

Python 3.13, FastAPI, Pydantic, SQLAlchemy (императивный маппинг), Alembic, Dishka, PostgreSQL 17, RustFS (S3), uv, pytest, ruff.

## Структура

```text
backend/
├── src/app/
│   ├── domain/         # сущности и бизнес-правила, без фреймворков
│   ├── application/    # интеракторы, DTO, порты
│   ├── infra/          # БД, шлюзы, JWT, S3, LLM, Web Push, PDF
│   └── presentation/   # роутеры FastAPI, схемы, middleware
├── alembic/versions/   # миграции, включая демо-данные жюри и админа
├── tests/              # тесты по уровням: api, unit, infra, scenarios...
├── scripts/            # Postman из OpenAPI, отчёт покрытия, ключи VAPID
└── docs/               # документы сдачи
```

Зависимости направлены внутрь: `presentation` → `infra` → `application` → `domain`.

## Запуск без Docker

Нужны [uv](https://docs.astral.sh/uv/), PostgreSQL с базой `petcare` и RustFS (или другой S3). Приложение читает настройки только из окружения процесса, `.env` не загружается. Справочник переменных — [`.env.example`](.env.example).

```bash
uv sync
uv run alembic upgrade head
uv run python -m app.run        # http://localhost:8080, Swagger — /docs
```

Весь стенд в Docker и переменные продакшена — в [`../deploy/README.md`](../deploy/README.md).

## Проверки

```bash
uv run pytest                   # все тесты на SQLite в памяти, БД и S3 не нужны
uv run ruff check .
sh scripts/coverage_report.sh   # покрытие требований и кода → reports/coverage.md
uv run python scripts/build_postman_collection.py   # пересобрать коллекцию после изменений API
```
