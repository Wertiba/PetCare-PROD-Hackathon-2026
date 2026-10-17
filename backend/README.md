# PetCare backend

Бэкенд на FastAPI: регистрация, питомцы, карта здоровья (события), учёт питания и параметров (категории и замеры), напоминания. Архитектура: `presentation` → `application` → `domain`; адаптеры находятся в `infra`. Маршруты и названия полей API сохранены; даты и моменты времени передаются и хранятся как Unix timestamp в секундах.

Код перенесён из ветки `backend/roma_crud` (коммит `3d9b36a`) в каталог `backend/`.

## Структура проекта

```text
backend/
├── src/app/        # код Python-пакета app
├── tests/          # тесты
├── alembic/        # миграции базы данных
├── configs/        # конфигурация приложения
├── alembic.ini
├── pytest.ini
├── ruff.toml
└── pyproject.toml
```

`uv sync` устанавливает пакет `app` из `src/` в editable-режиме.
Команды ниже запускаются из `backend/`; переходить в `src/` не требуется.
`.env`, `logs/` и `media/` находятся в `backend/` и не входят в исходный код.

## Архитектура

- `src/app/domain` — обычные Python-сущности, перечисления, ошибки и бизнес-правила; без SQLAlchemy и FastAPI. Код сгруппирован по сущностям: например, `domain/pets/entity.py`, `enums.py`, `rules.py` и `errors.py`.
- `src/app/application` — отдельный интерактор для каждой операции, dataclass-входы и результаты, интерфейсы шлюзов и внешних сервисов. Провайдеры Dishka находятся рядом с интеракторами в `di.py`.
- `src/app/infra` — SQLAlchemy-маппинг сущностей, шлюзы чтения, работа с токенами, файлами и метриками. Маппинг императивный: доменные сущности не наследуются от ORM-классов.
- `src/app/presentation/http` — маршруты FastAPI, Pydantic-схемы, HTTP-валидация, cookie и middleware. `app.main:app` остаётся точкой входа.

Unit of Work — тонкий прокси с асинхронными `add(entity)`, `delete(entity)` и `commit()`. Интерактор читает сущности через шлюзы, изменяет их поля и явно вызывает `commit()`. Читающие операции не коммитят. Репозитории и контекстный менеджер у UoW отсутствуют.

Каждый шлюз реализует конкретные методы чтения (`get_by_id`, `get_by_login`, `get_by_user_id` и т. п.) и самостоятельно получает сессию. Общего generic-шлюза нет. Параметры поиска передаются явными аргументами; классов FilterQuery нет. Ошибки приложения и адаптеров наследуются от `ApplicationError`; нарушение уникальности представлено `DuplicateError`.

Dishka предоставляет одну SQLAlchemy-сессию на запрос: авторизация, шлюзы и UoW используют её совместно. Провайдер сессии откатывает незавершённую транзакцию и закрывает сессию; lifespan приложения закрывает контейнер и освобождает движок БД. Настройка зависимостей собрана в `app/bootstrap.py`.

Регистрация с выдачей токенов, ротация refresh-токена и завершение повторяющегося события записываются одной транзакцией. HTTP-обработчики публикуют метрики успешных действий после завершения интерактора и коммита; при сбое загрузки фото новый файл удаляется, а старый сохраняется.

## Запуск

Нужен Postgres. Базу `petcare` создайте заранее. Зависимости ставятся через [uv](https://docs.astral.sh/uv/) из каталога `backend/`.

```bash
cd backend
uv sync
cp .env.example .env
```

В `.env` пропишите доступ к базе и свой `APP_SECURITY_JWT_SECRET`. Для локального HTTP поставьте `APP_COOKIE_SECURE=false`, иначе браузер не сохранит refresh-cookie.

```bash
uv run alembic upgrade head
uv run python -m app.run
```

Для существующей базы миграция `0004_epoch_timestamps` переводит все поля времени в `DOUBLE PRECISION`, сохраняя их значения как секунды от Unix epoch. Дата рождения преобразуется в полночь UTC. Откат миграции восстанавливает типы timestamp/date. Миграция выполняется обычной командой `alembic upgrade head` до запуска новой версии приложения.

Миграция `0005_user_login` переименовывает идентификатор существующих пользователей в `login`, сохраняя значения и уникальность. Существующий идентификатор продолжает работать как логин; отдельного поля почты и проверки адреса нет.

Сервис слушает `http://localhost:8080`. Список методов и схемы запросов: `http://localhost:8080/docs`.

Миграция `0003` создаёт встроенные категории (вес, корм, вода, прогулка, аппетит, «корм понравился», «корм подошёл», «проблемы с ЖКТ», «аллергическая реакция» и др.) — они видны всем пользователям и доступны только на чтение.

## Авторизация

`POST /api/v1/auth/register` принимает `login`, `password`, `fullName`; `POST /api/v1/auth/login` — `login` и `password`. Логин — непустая строка до 255 символов, уникальная с учётом регистра. Пользователь в ответах содержит `login`. Дублирующий логин возвращает `409 LOGIN_ALREADY_EXISTS`. Оба метода возвращают `accessToken`. Его передают заголовком `Authorization: Bearer <token>`.

Refresh-токен приходит в HttpOnly-cookie `refreshToken`. Обновить access: `POST /api/v1/auth/refresh`. Выйти: `POST /api/v1/auth/logout`.

## Методы

Все списки принимают `page` (с 0) и `size` (1–100) и отвечают `{items, page, size, total}`. Все моменты времени — числовые Unix seconds в UTC, например `1770000000.125`: в теле запроса, query-параметрах и ответах. Это относится к `createdAt`, `updatedAt`, `schedule`, `doneAt`, `nextSchedule`, `time`, `from`, `to`, `birthDate` и `timestamp` в ошибках. `birthDate` нормализуется к полуночи UTC. ISO-строки дат больше не принимаются. Продолжительности (`expiresIn`, `days`, `ageMonths`) сохраняют свои единицы. Используются обычные `float` и стандартные модули Python `time`, `datetime`, `calendar`. Чужие и несуществующие объекты отвечают `404`. Ссылка в теле запроса на чужой/несуществующий объект (`petId`, `catId`, `eventId`) — `422` с `code` вида `PET_NOT_FOUND` и `details.field`.

| Метод | Путь | Что делает |
|---|---|---|
| GET | `/health/liveness`, `/health/readiness` | Процесс жив, база отвечает |
| GET | `/metrics` | Метрики Prometheus |
| POST | `/api/v1/auth/register`, `/login`, `/refresh`, `/logout` | Авторизация |
| GET / PATCH | `/api/v1/users/me` | Профиль, смена `fullName` |
| GET | `/api/v1/breeds?type=&q=` | Породы |
| GET / POST | `/api/v1/pets` | Свои питомцы / создать (`name`, `type`) |
| GET / PATCH / DELETE | `/api/v1/pets/{petId}` | Карточка. Удаление каскадно удаляет события, замеры, уведомления |
| PUT | `/api/v1/pets/{petId}/photo` | Фото, поле формы `file`. jpeg, png или webp, до 5 МБ |
| GET / POST | `/api/v1/categories?type=&q=` | Встроенные + свои категории / создать свою |
| GET / PATCH / DELETE | `/api/v1/categories/{id}` | Встроенные менять нельзя — `403 SYSTEM_CATEGORY_READ_ONLY` |
| GET / POST | `/api/v1/states?petId=&catId=&from=&to=` | Замеры (вес, корм, реакции...) |
| GET | `/api/v1/states/summary?petId=&catId=&from=&to=` | Агрегат за период по `kind` категории: sum, avg, last, count, min, max |
| GET / PATCH / DELETE | `/api/v1/states/{id}` | Замер |
| GET / POST | `/api/v1/events?petId=&status=&type=&from=&to=` | События: прививки, обработки, визиты к ветеринару, лекарства |
| GET | `/api/v1/events/upcoming?days=30&petId=` | Ближайшие запланированные, включая просроченные (`isOverdue`) |
| GET / PATCH / DELETE | `/api/v1/events/{id}` | Событие |
| POST | `/api/v1/events/{id}/complete` | Отметить выполненным, тело `{doneAt?}`. Для повторяющегося создаёт следующее |
| GET / POST | `/api/v1/notifications?eventId=&petId=&status=&due=` | Уведомления. `due=true` — pending, время которых наступило |
| GET / PATCH / DELETE | `/api/v1/notifications/{id}` | Уведомление (например, `{"status": "read"}`) |

### Правила предметной области

- **Значение замера** проверяется по типу категории: `check` — 0 или 1, `scale` — от 1 до 5, `number` — не меньше 0. Иначе `422 INVALID_VALUE`.
- **Повторяющиеся события** (`period`: daily, weekly, monthly, quarterly, half_year, yearly). В ответе есть `nextSchedule`. Когда запланированное событие отмечают выполненным (через `/complete` или `PATCH status=done`), сервис создаёт следующее. Дата считается от более поздней из двух: плановой или фактической (`doneAt`). Прививку, сделанную на два месяца позже плана, в следующий раз нужно делать через год от фактической даты.
- **Тип события** (`type`): vaccination, parasite_treatment, vet_visit, medication, grooming, other. По нему строится карта здоровья: `GET /events?petId=...&type=vaccination`.

## Наблюдаемость

- **Логи** (loguru) — в stdout и в `logs/petcare.log`. В каждой строке есть `trace_id`. Его берут из заголовка `X-Trace-Id` или генерируют, а затем возвращают в том же заголовке и в теле ошибок (`traceId`). На каждый запрос пишется одна строка: метод, путь, статус, время.
- **Метрики** на `/metrics`: `petcare_http_requests_total{method,path,status}`, `petcare_http_request_duration_seconds`, `petcare_http_requests_in_progress` и бизнес-счётчик `petcare_domain_events_total{entity,action}` (регистрации, созданные питомцы, выполненные события и т. п.). `path` — шаблон маршрута, например `/api/v1/pets/{pet_id}`.
- **Ошибки** приходят в одном формате: `{code, message, traceId, timestamp, path, details?}`. Ошибки валидации — `422` с `fieldErrors`. Непредвиденное исключение — `500 INTERNAL_ERROR`, стектрейс пишется в лог.

## Проверка

Из каталога `backend`:

```bash
uv run python -m pytest
uv run ruff check .
```

Тесты идут на SQLite в памяти с включёнными внешними ключами. `.env` им не нужен: тестовые значения подставляет `tests/conftest.py`. Отдельных тестовых контейнеров и фабрик приложения нет. Контракт API сравнивается с `docs/openapi.json`, а определения таблиц и индексов PostgreSQL — с сохранённым снимком. Проверяются также границы слоёв, откаты транзакций, общая сессия запроса, дробные timestamp, epoch zero, календарные повторы и SQL прямой/обратной миграции. На виртуальную машину тесты не выкладываются.

## Docker и деплой

Из корня репозитория образ собирается командой `docker build -t petcare-backend backend`.
Контейнер применяет миграции перед запуском API на порту `8000`. Проверка готовности —
`/health/readiness`.

Корневой `docker-compose.yaml` запускает PostgreSQL, backend, frontend и Caddy.
В корневом `.env` задайте `DOMAIN`, `FRONTEND_IMAGE`, `BACKEND_IMAGE`, `DB_PASSWORD`
и `APP_SECURITY_JWT_SECRET` (см. `.env.example`), затем выполните `docker compose up -d`.
Для CI/CD добавьте `DB_PASSWORD` и `APP_SECURITY_JWT_SECRET` в защищённые переменные GitLab.
Данные PostgreSQL и фотографии питомцев хранятся в отдельных Docker volumes.
