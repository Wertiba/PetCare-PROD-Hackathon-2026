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

## Структурированные логи

Backend использует стандартный модуль Python `logging` и пишет по одному JSON-объекту
в строке stdout для сбора Vector. Каждая запись содержит обязательные поля Sage:
`env` (`LOG_ENV`, по умолчанию `dev`), `system` (`LOG_SYSTEM`, `petcare`),
`inst` (`LOG_INST`, по умолчанию hostname контейнера), `@timestamp` (UTC).
Production Compose задаёт `LOG_ENV=prod`; настройки передаются также из GitLab CI.
`LOG_CONSOLE_LEVEL` управляет уровнем логирования (по умолчанию `INFO`).
`LOG_ENV` и `LOG_SYSTEM` должны соответствовать `^[a-z][a-z0-9_-]*$`,
`LOG_INST` — `^[a-zA-Z0-9][a-zA-Z0-9_.-]*$`; неверные значения останавливают запуск.

HTTP-записи содержат `event`, `http_method`, `route` (шаблон маршрута), `status_code`,
`duration_ms`, UUID `trace_id` и доступные UUID ресурсов. Успешные health-check
и scrape метрик не логируются. Произвольный `X-Trace-Id` сохраняется в ответе API,
но для логов заменяется отдельным UUID; входящий UUID используется для корреляции.
Ошибки фоновой доставки содержат UUID уведомления, события и питомца, канал и
код причины; сбой опроса — интервал следующей попытки.

Новые события добавляйте в каталог `_EVENTS` в `app/infra/logger.py` и вызывайте
`logging.getLogger(__name__).info("event_name", extra={...})`. Сообщения статичны;
дополнительные поля допускаются только по явному списку. Не передавайте имена,
логины, тексты заметок, тела запросов/ответов, заголовки, cookie, токены, подписанные
URL или ключи. Ошибки записывают тип и расположение кадров стека, без текста
исключений, строк исходного кода или локальных переменных. Неструктурированные
сообщения зависимостей ниже ERROR отбрасываются; ошибки зависимостей получают
фиксированное сообщение. SQL echo отключён, параметры SQL скрыты. Старые настройки
`LOG_CONSOLE_FORMAT`, `LOG_CONSOLE_ENQUEUE`, `LOG_CONSOLE_BACKTRACE`,
`LOG_CONSOLE_DIAGNOSE`, `DB_ECHO`, `DB_ECHO_POOL` больше не используются.

### Vector → Sage в production

Vector запускается отдельным сервисом `vector` в production Compose; локальный
`compose.local.yaml` не отправляет логи в Sage. Конфигурация — `deploy/vector.yaml`,
образ закреплён на `timberio/vector:0.59.0-debian`.

В GitLab CI задайте `SAGE_GROUP=hack-led-15` и **masked, protected** переменную
`SAGE_API_KEY` со значением Spirit API key **без** префикса `JWT`. Pipeline записывает
оба значения в `.env` на сервере с правами `600`; Compose передаёт их только
контейнеру Vector. Ключ не попадает в окружение backend или логи CI. Vector 0.59
использует `VECTOR_DANGEROUSLY_ALLOW_ENV_VAR_INTERPOLATION=true`, чтобы подставлять
`${SAGE_GROUP}` и `${SAGE_API_KEY}` в конфигурацию. CI проверяет конфигурацию
с тестовыми значениями без обращения к Sage. Временный `.env.deploy` удаляется
после выполнения job; `.env` исключён из Git.

На защищённой production-ветке выполните обычный pipeline: он проверяет
конфигурацию, копирует её на сервер и запускает Vector вместе с приложением.
При ручном запуске production Compose задайте `SAGE_GROUP` и `SAGE_API_KEY`
в корневом `.env` или в окружении терминала и выполните:

```bash
docker compose up -d --wait
```

Путь данных: stdout backend → Docker logs → извлечение JSON из поля `message`
→ HTTP POST `https://sage.spirit.t-education.com/api/<SAGE_GROUP>/multiline`
с заголовком `Authorization: JWT <key>`. Vector отправляет JSON-объекты через `\n`,
до 100 событий или 1 МБ в батче, не реже одного раза в секунду при наличии данных.
Успешная загрузка возвращает HTTP 200. Проверка GET/HEAD отключена: endpoint
принимает POST и отвечает Method Not Allowed при открытии в браузере.

Собирается только backend с меткой `petcare.vector.logs=true`. Его метка
`sage.agent.logs=false` предотвращает параллельную доставку через Sage Agent,
если агент восстановится. Метки остальных сервисов сохранены. Docker wrapper,
labels и hostname коллектора удаляются. Vector только извлекает JSON приложения;
проверка полей и времени остаётся за приложением и Sage. Строки, которые не удаётся
разобрать как JSON, отбрасываются без отправки оригинала.
Vector использует Docker socket; монтирование `:ro` не ограничивает права Docker
API, поэтому доступ к этому контейнеру должен быть таким же доверенным, как к Docker.

Буфер до 512 МиБ хранится в volume `vector_data` и сохраняется при пересоздании
Vector. Повторные попытки покрывают временные сетевые ошибки, 429 и 5xx;
ошибки авторизации 401/403 требуют исправления ключа. Это не гарантия доставки
без потерь: при остановленном коллекторе или заполнении буфера возможны пропуски,
а после сбоев возможны дубликаты. Не удаляйте `vector_data`, если в нём есть
неотправленные записи.

После деплоя проверьте:

```bash
docker compose ps vector
docker compose logs --tail=50 vector
```

Выполните обычный запрос к API и найдите его в Sage:
`group = "hack-led-15" system = "petcare" env = "prod"`.
Если логов нет, проверьте ответы 401/403/429/5xx в логах Vector и индекс dead-letters
в Sage. Не включайте отладочное логирование HTTP-заголовков или payload.
