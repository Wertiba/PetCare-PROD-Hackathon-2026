# PetCare backend

Бэкенд на FastAPI: регистрация, питомцы, карта здоровья (события), учёт питания и параметров (категории и замеры), напоминания. Слои: `api` → `services` → `infrastructure` (репозитории + Unit of Work) → Postgres.

Docker и описание деплоя здесь нет. Их добавляют отдельно, когда сервис выкладывают на виртуальную машину.

## Запуск

Нужен Postgres. Базу `petcare` создайте заранее. Зависимости ставятся через [uv](https://docs.astral.sh/uv/) из корня репозитория.

```bash
uv sync
cp src/.env.example src/.env
```

В `src/.env` пропишите доступ к базе и свой `APP_SECURITY_JWT_SECRET`. Для локального HTTP поставьте `APP_COOKIE_SECURE=false`, иначе браузер не сохранит refresh-cookie.

```bash
cd src
uv run alembic upgrade head
uv run python -m app.run
```

Сервис слушает `http://localhost:8080`. Список методов и схемы запросов: `http://localhost:8080/docs`.

Миграция `0003` создаёт встроенные категории (вес, корм, вода, прогулка, аппетит, «корм понравился», «корм подошёл», «проблемы с ЖКТ», «аллергическая реакция» и др.) — они видны всем пользователям и доступны только на чтение.

## Авторизация

`POST /api/v1/auth/register` и `POST /api/v1/auth/login` возвращают `accessToken`. Его передают заголовком `Authorization: Bearer <token>`.

Refresh-токен приходит в HttpOnly-cookie `refreshToken`. Обновить access: `POST /api/v1/auth/refresh`. Выйти: `POST /api/v1/auth/logout`.

## Методы

Все списки принимают `page` (с 0) и `size` (1–100) и отвечают `{items, page, size, total}`. Даты — ISO-8601 в UTC с `Z`. Чужие и несуществующие объекты отвечают `404`. Ссылка в теле запроса на чужой/несуществующий объект (`petId`, `catId`, `eventId`) — `422` с `code` вида `PET_NOT_FOUND` и `details.field`.

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

- **Логи** (loguru) — в stdout и в `src/logs/petcare.log`. В каждой строке есть `trace_id`. Его берут из заголовка `X-Trace-Id` или генерируют, а затем возвращают в том же заголовке и в теле ошибок (`traceId`). На каждый запрос пишется одна строка: метод, путь, статус, время.
- **Метрики** на `/metrics`: `petcare_http_requests_total{method,path,status}`, `petcare_http_request_duration_seconds`, `petcare_http_requests_in_progress` и бизнес-счётчик `petcare_domain_events_total{entity,action}` (регистрации, созданные питомцы, выполненные события и т. п.). `path` — шаблон маршрута, например `/api/v1/pets/{pet_id}`.
- **Ошибки** приходят в одном формате: `{code, message, traceId, timestamp, path, details?}`. Ошибки валидации — `422` с `fieldErrors`. Непредвиденное исключение — `500 INTERNAL_ERROR`, стектрейс пишется в лог.

## Проверка

Из каталога `src`:

```bash
uv run python -m pytest
uv run ruff check .
```

Тесты идут на SQLite в памяти с включёнными внешними ключами. `.env` им не нужен: тестовые значения подставляет `tests/conftest.py`. На виртуальную машину тесты не выкладываются.
