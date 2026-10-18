# PetCare backend

Бэкенд на FastAPI: регистрация, питомцы, карта здоровья (события), учёт питания и параметров (категории и замеры), напоминания. Архитектура: `presentation` → `application` → `domain`; адаптеры находятся в `infra`. Маршруты и названия полей API сохранены; даты и моменты времени передаются и хранятся как Unix timestamp в секундах.

Код перенесён из ветки `backend/roma_crud` (коммит `3d9b36a`) в каталог `backend/`.

Архитектура, диаграммы C4, карта эндпоинтов и отчёты о тестах: [`docs/architecture.md`](docs/architecture.md).

## Структура проекта

```text
backend/
├── src/app/        # код Python-пакета app
├── tests/          # тесты
├── alembic/        # миграции базы данных
├── alembic.ini
├── pytest.ini
├── ruff.toml
└── pyproject.toml
```

`uv sync` устанавливает пакет `app` из `src/` в editable-режиме.
Команды ниже запускаются из `backend/`; переходить в `src/` не требуется.
Логи выводятся в stdout. Фотографии хранятся в RustFS.

## Архитектура

- `src/app/domain` — обычные Python-сущности, перечисления, ошибки и бизнес-правила; без SQLAlchemy и FastAPI. Код сгруппирован по сущностям: например, `domain/pets/entity.py`, `enums.py`, `rules.py` и `errors.py`.
- `src/app/application` — отдельный интерактор для каждой операции, dataclass-входы и результаты, интерфейсы шлюзов и внешних сервисов. Провайдеры Dishka находятся рядом с интеракторами в `di.py`.
- `src/app/infra` — SQLAlchemy-маппинг сущностей, шлюзы чтения, работа с токенами, файлами и метриками. Маппинг императивный: доменные сущности не наследуются от ORM-классов.
- `src/app/presentation/http` — маршруты FastAPI, Pydantic-схемы, HTTP-валидация, cookie и middleware. `app.main:app` остаётся точкой входа.

Unit of Work — тонкий прокси с асинхронными `add(entity)`, `delete(entity)` и `commit()`. Интерактор читает сущности через шлюзы, изменяет их поля и явно вызывает `commit()`. Читающие операции не коммитят. Репозитории и контекстный менеджер у UoW отсутствуют.

Каждый шлюз реализует конкретные методы чтения (`get_by_id`, `get_by_login`, `get_by_user_id` и т. п.) и самостоятельно получает сессию. Общего generic-шлюза нет. Параметры поиска передаются явными аргументами; классов FilterQuery нет. Ошибки приложения и адаптеров наследуются от `ApplicationError`; нарушение уникальности представлено `DuplicateError`.

Dishka предоставляет одну SQLAlchemy-сессию на запрос: авторизация, шлюзы и UoW используют её совместно. Провайдер сессии откатывает незавершённую транзакцию и закрывает сессию; lifespan приложения закрывает контейнер и освобождает движок БД. Настройка зависимостей собрана в `app/bootstrap.py`.

Регистрация с выдачей токенов, ротация refresh-токена и завершение повторяющегося события записываются одной транзакцией. HTTP-обработчики публикуют метрики успешных действий после завершения интерактора и коммита; при сбое загрузки фото или аватара новый объект удаляется, а старые сохраняются.

## Запуск

Нужен Postgres. Базу `petcare` создайте заранее. Зависимости ставятся через [uv](https://docs.astral.sh/uv/) из каталога `backend/`.

```bash
cd backend
uv sync
```

Перед запуском экспортируйте переменные подключения к БД, `APP_SECURITY_JWT_SECRET`
и `S3_*` в окружение процесса. `backend/.env.example` — справочник переменных,
он не загружается автоматически. Для локального HTTP задайте
`APP_COOKIE_SECURE=false`, иначе браузер не сохранит cookie токенов.

Все конфигурации — обычные Pydantic `BaseModel` с полями и значениями по умолчанию.
Каждое поле содержит явный `Field(alias="ИМЯ_ПЕРЕМЕННОЙ")`. Модели создаются
через `Model(**os.environ)` в `ConfigProvider` и предоставляются Dishka в `Scope.APP`.
`create_app` в `main.py` получает `AppConfig`, `HttpConfig` и логирование через
`container.get_sync`, затем передаёт тот же контейнер FastAPI. JWT, фотографии,
cookie и база получают свои конфигурации из этого контейнера. Движок БД и S3-клиенты
создаются провайдерами по требованию и закрываются при завершении lifespan.
Приложение и Alembic не читают `.env` или YAML; `BaseSettings`, dotenv-загрузчики
и `env_file` Pydantic не используются. Значения для production задаются в CI.

| Настройки | Переменные окружения |
|---|---|
| Имя приложения | `APP_NAME` |
| Самостоятельный запуск API | `RUN_HOST`, `RUN_PORT` |
| PostgreSQL | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_DRIVER`, `DB_ECHO`, `DB_ECHO_POOL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` |
| JWT и пароли | `APP_SECURITY_JWT_SECRET`, `APP_SECURITY_ACCESS_TOKEN_EXPIRATION`, `APP_SECURITY_REFRESH_TOKEN_EXPIRATION`, `APP_SECURITY_PASSWORD_SCHEME`, `APP_SECURITY_ALGORITHM` |
| Cookie и CORS | `APP_COOKIE_SECURE`, `APP_CORS_ALLOWED_ORIGINS` |
| Логи в stdout | `LOG_CONSOLE_LEVEL`, `LOG_CONSOLE_ENQUEUE`, `LOG_CONSOLE_BACKTRACE`, `LOG_CONSOLE_DIAGNOSE`, `LOG_CONSOLE_FORMAT` |
| Фотографии | `S3_*` (описаны ниже) |
| Внешние напоминания | `NOTIFICATIONS_*`, `VAPID_*` (см. [docs/notifications.md](docs/notifications.md)) |

Миграциям нужны только настройки `DB_*`, инициализатору хранилища — только `S3_*`
и `RUSTFS_ACCESS_KEY`/`RUSTFS_SECRET_KEY`. Они не требуют остальные конфигурации.

```bash
uv run alembic upgrade head
uv run python -m app.run
```

Для существующей базы миграция `0004_epoch_timestamps` переводит все поля времени в `DOUBLE PRECISION`, сохраняя их значения как секунды от Unix epoch. Дата рождения преобразуется в полночь UTC. Откат миграции восстанавливает типы timestamp/date. Миграция выполняется обычной командой `alembic upgrade head` до запуска новой версии приложения.

Миграция `0005_user_login` переименовывает идентификатор существующих пользователей в `login`, сохраняя значения и уникальность. Существующий идентификатор продолжает работать как логин; отдельного поля почты и проверки адреса нет.

Сервис слушает `http://localhost:8080`. Список методов и схемы запросов: `http://localhost:8080/docs`.

Миграция `0003` создаёт встроенные категории (вес, корм, вода, прогулка, аппетит, «корм понравился», «корм подошёл», «проблемы с ЖКТ», «аллергическая реакция» и др.) — они видны всем пользователям и доступны только на чтение.

## Авторизация

`POST /api/v1/auth/register` принимает `login`, `password`, `fullName`; `POST /api/v1/auth/login` — `login` и `password`. Логин — непустая строка до 255 символов, уникальная с учётом регистра. Пользователь в ответах содержит `login`. Дублирующий логин возвращает `409 LOGIN_ALREADY_EXISTS`.

Регистрация, вход и `POST /api/v1/auth/refresh` устанавливают HttpOnly-cookie `accessToken` и `refreshToken` с `SameSite=Lax`, `Path=/` и флагом `Secure` из `APP_COOKIE_SECURE`. Срок жизни access-cookie равен `expiresIn`, refresh-cookie — сроку refresh-токена. Защищённые методы принимают access-cookie; заголовок `Authorization: Bearer <token>` по-прежнему поддерживается и имеет приоритет, если передан. Некорректный заголовок не заменяется cookie. `POST /api/v1/auth/logout` отзывает refresh-токен и удаляет обе cookie.

Тела ответов сохранены: `accessToken`, `expiresIn` и `user` (для регистрации и входа). Поле `accessToken` помечено `deprecated` в OpenAPI/Swagger с предупреждением об удалении из тела в будущей версии API; дата удаления пока не назначена. Новый frontend должен использовать cookie и включать `credentials: "include"` для запросов с другого разрешённого origin. Предупреждение находится в документации API, автоматически в консоли браузера оно не появляется.

## Postman

Коллекция: `docs/petcare.postman_collection.json` (Import в Postman). `baseUrl` по умолчанию `http://localhost:8080`.
Порядок: Auth → Login (`жюри1` / `qwerty12345`) сохраняет токен, каждый POST сохраняет id созданного объекта, удаления собраны в папке Cleanup в конце.
После изменений API: `uv run python scripts/build_postman_collection.py`.

## Методы

Все списки принимают `page` (с 0) и `size` (1–100) и отвечают `{items, page, size, total}`. Все моменты времени — числовые Unix seconds в UTC, например `1770000000.125`: в теле запроса, query-параметрах и ответах. Это относится к `createdAt`, `updatedAt`, `schedule`, `doneAt`, `nextSchedule`, `time`, `from`, `to`, `birthDate` и `timestamp` в ошибках. `birthDate` нормализуется к полуночи UTC. ISO-строки дат больше не принимаются. Продолжительности (`expiresIn`, `days`, `ageMonths`) сохраняют свои единицы. Используются обычные `float` и стандартные модули Python `time`, `datetime`, `calendar`. Чужие и несуществующие объекты отвечают `404`. Ссылка в теле запроса на чужой/несуществующий объект (`petId`, `categoryId`, `eventId`, `breedId`, `animalId`) — `422` с `code` вида `PET_NOT_FOUND` и `details.field`.

| Метод | Путь | Что делает |
|---|---|---|
| GET | `/health/liveness`, `/health/readiness` | Процесс жив, база отвечает |
| GET | `/metrics` | Метрики Prometheus |
| POST | `/api/v1/auth/register`, `/login`, `/refresh`, `/logout` | Авторизация |
| GET / PATCH | `/api/v1/users/me` | Профиль, смена `fullName` |
| GET / POST | `/api/v1/animals?q=` | Виды животных. Создавать, менять и удалять может только админ (`403 FORBIDDEN`) |
| GET / PATCH / DELETE | `/api/v1/animals/{id}` | Вид. Удаление удаляет его породы, питомцы остаются без породы |
| GET / POST | `/api/v1/breeds?animalId=&q=` | Породы. Сначала стартовые из миграции. Запись только админу |
| GET / PATCH / DELETE | `/api/v1/breeds/{id}` | Порода. Удаление оставляет питомцев без породы |
| GET / POST | `/api/v1/pets` | Свои питомцы / создать (`name`, `breedId`, `birthDate?`). Вид берётся из породы |
| GET / PATCH / DELETE | `/api/v1/pets/{petId}` | Карточка с `animal` и `breed`. Удаление каскадно удаляет события, замеры, уведомления, заметки, корма |
| PUT | `/api/v1/pets/{petId}/photo` | Фото, поле формы `file`. jpeg, png или webp, до 5 МБ. Новое фото сбрасывает сгенерированный аватар |
| POST | `/api/v1/pets/{petId}/photo/upload-url` | Подписанная ссылка, чтобы браузер загрузил jpeg/png/webp (до 5 МБ) напрямую. В базе ничего не меняет |
| POST | `/api/v1/pets/{petId}/photo/confirm` | Принять объект `{key}` после прямой загрузки. Новое фото сбрасывает сгенерированный аватар |
| DELETE | `/api/v1/pets/{petId}/photo` | Удалить фото и аватар, собранный из него |
| POST | `/api/v1/pets/{petId}/avatar/generate` | Стилизованный аватар по уже загруженному фото. Необязательный `prompt` — короткое пожелание по внешнему виду. `avatarSource` не меняется |
| PUT | `/api/v1/pets/{petId}/avatar` | Какую картинку показывать: `{"source": "photo"}` или `{"source": "generated"}` |
| DELETE | `/api/v1/pets/{petId}/avatar/generated` | Удалить только сгенерированный аватар. Если он был выбран, показ возвращается на фото |
| GET | `/api/v1/pets/{petId}/report` | PDF-отчёт: ближайшие процедуры, прививки и обработки, активность по месяцам, график веса, самочувствие, корма и заключения врачей |
| GET / POST | `/api/v1/categories?type=&q=` | Общие для всех категории: встроенные, затем созданные пользователями / создать |
| GET / PATCH / DELETE | `/api/v1/categories/{id}` | Менять может автор или админ (иначе `403`, для встроенных `SYSTEM_CATEGORY_READ_ONLY`). Пока категорией пользуются другие, нельзя удалить её или сменить `kind`/`type`: `409 CATEGORY_IN_USE` |
| GET / POST | `/api/v1/states?petId=&categoryId=&from=&to=` | Замеры (вес, корм, реакции...) |
| GET | `/api/v1/states/summary?petId=&categoryId=&from=&to=` | Агрегат за период по `kind` категории: sum, avg, last, count, min, max |
| GET / PATCH / DELETE | `/api/v1/states/{id}` | Замер |
| GET / POST | `/api/v1/events?petId=&status=&type=&from=&to=` | События: прививки, обработки, визиты к ветеринару, лекарства |
| GET | `/api/v1/events/upcoming?days=30&petId=` | Ближайшие запланированные, включая просроченные (`isOverdue`) |
| GET | `/api/v1/events/calendar.ics?petId=&alarmMinutes=1440&until=` | Файл `.ics` для календаря телефона: запланированные события до `until` |
| GET / PATCH / DELETE | `/api/v1/events/{id}` | Событие |
| POST | `/api/v1/events/{id}/complete` | Отметить выполненным, тело `{doneAt?}`. Для повторяющегося создаёт следующее |
| GET / POST | `/api/v1/notifications?eventId=&petId=&status=&due=` | Уведомления. `due=true` — pending, время которых наступило |
| GET / PATCH / DELETE | `/api/v1/notifications/{id}` | Уведомление (например, `{"status": "read"}`). `deliveredAt` — внешняя доставка, `status` по-прежнему для тостов в приложении |
| GET / PATCH | `/api/v1/notifications/settings` | Канал Web Push |
| GET | `/api/v1/notifications/web-push/public-key` | Публичный VAPID-ключ |
| POST / DELETE | `/api/v1/notifications/web-push/subscriptions` | Подписка браузера |
| POST | `/api/v1/notifications/test` | Проверочное сообщение в Web Push, если канал включён |
| GET / POST | `/api/v1/notes?petId=&q=` | Текстовые заметки в карточке питомца, новые сначала |
| GET / PATCH / DELETE | `/api/v1/notes/{id}` | Заметка |
| GET / POST | `/api/v1/foods?petId=&isApproach=&isTolerability=` | Журнал кормлений: `name`, `weight` (г), `ingredients`, `isApproach` (понравилось), `isTolerability` (подошло), `consequences` (реакция) |
| GET / PATCH / DELETE | `/api/v1/foods/{id}` | Кормление |
| GET | `/api/v1/foods/{id}/suspects` | Ингредиенты этого корма, которых не было ни в одном ранее съеденном корме с `isTolerability=true` |

### Правила предметной области

- **Аккаунты жюри** `жюри1`…`жюри10` с паролем `qwerty12345` создаёт миграция `0007` (для кнопок быстрого входа на фронте), а `0009` наполняет их историей: у каждого 2–3 своих питомца, просроченные и ближайшие процедуры, замеры за год, журнал кормов, заметки. Даты отсчитываются от момента применения миграции.
- **Админ** — пользователь с `role = 'ADMIN'`. Через API роль не выдаётся: `UPDATE users SET role = 'ADMIN' WHERE login = '...'`.
- **Подозрительные ингредиенты.** Сравнение без учёта регистра и лишних пробелов. Если у питомца ещё не было подошедших кормов, подозрительны все ингредиенты. Ингредиенты при сохранении очищаются от пустых строк и повторов.

- **Значение замера** проверяется по типу категории: `check` — 0 или 1, `scale` — от 1 до 5, `number` — не меньше 0. Иначе `422 INVALID_VALUE`.
- **Повторяющиеся события** (`period`: daily, weekly, monthly, quarterly, half_year, yearly). В ответе есть `nextSchedule`. Когда запланированное событие отмечают выполненным (через `/complete` или `PATCH status=done`), сервис создаёт следующее. Дата считается от более поздней из двух: плановой или фактической (`doneAt`). Прививку, сделанную на два месяца позже плана, в следующий раз нужно делать через год от фактической даты.
- **Тип события** (`type`): vaccination, parasite_treatment, vet_visit, medication, grooming, other. По нему строится карта здоровья: `GET /events?petId=...&type=vaccination`.

## Внешние напоминания

Web Push не меняет `status`: фронт по-прежнему опрашивает `GET /notifications?due=true` и сам отмечает прочитанным. Внешняя отправка пишется в `deliveredAt`. Пользователь включает Web Push в настройках и регистрирует подписку браузера. Переменные и ключи VAPID описаны в [docs/notifications.md](docs/notifications.md).

## Календарь

`GET /api/v1/events/calendar.ics` отдаёт файл `.ics` с запланированными событиями. Контракт, поля файла и пример скачивания — в [docs/calendar.md](docs/calendar.md).

## Фото и аватар

Загрузка фото, генерация аватара по этому фото и выбор, что показывать. Подробности для фронта и деплоя — в [docs/avatar.md](docs/avatar.md).

| Метод | Путь | |
|---|---|---|
| PUT | `/api/v1/pets/{petId}/photo` | Фото, поле `file`. jpeg/png/webp, до 5 МБ |
| POST | `/api/v1/pets/{petId}/photo/upload-url` | Подписанный `PUT` для прямой загрузки. В базе ничего не меняет |
| POST | `/api/v1/pets/{petId}/photo/confirm` | Принять загруженный `{key}` |
| DELETE | `/api/v1/pets/{petId}/photo` | Удалить фото и аватар из него |
| POST | `/api/v1/pets/{petId}/avatar/generate` | Аватар по загруженному фото. Необязательный `prompt` только про внешний вид. Выбор не меняет |
| PUT | `/api/v1/pets/{petId}/avatar` | `{"source": "photo"}` или `{"source": "generated"}` |
| DELETE | `/api/v1/pets/{petId}/avatar/generated` | Удалить только аватар. Показ возвращается на фото |

Показывать `avatarUrl`. Фотографии и аватары хранятся в приватном RustFS через
`PhotosGateway` на aioboto3. Генерация — Spirit LLM Proxy, ключ `LLM_PROXY_API_KEY`.
Конфигурация генерации — отдельная Pydantic-модель `AvatarConfig`, которую предоставляет Dishka.

## Наблюдаемость

- **Логи** (loguru) — в stdout. В каждой строке есть `trace_id`. Его берут из заголовка `X-Trace-Id` или генерируют, а затем возвращают в том же заголовке и в теле ошибок (`traceId`). На каждый запрос пишется одна строка: метод, путь, статус, время.
- **Метрики** на `/metrics`: `petcare_http_requests_total{method,path,status}`, `petcare_http_request_duration_seconds`, `petcare_http_requests_in_progress` и бизнес-счётчик `petcare_domain_events_total{entity,action}` (регистрации, созданные питомцы, выполненные события и т. п.). `path` — шаблон маршрута, например `/api/v1/pets/{pet_id}`.
- **Ошибки** приходят в одном формате: `{code, message, traceId, timestamp, path, details?}`. Ошибки валидации — `422` с `fieldErrors`. Непредвиденное исключение — `500 INTERNAL_ERROR`, стектрейс пишется в лог.

## Проверка

Из каталога `backend`:

```bash
uv run python -m pytest
uv run ruff check .
```

Покрытие требований и кода: `uv run pytest --cov`; отчёт `docs/coverage.md` обновляет `sh scripts/coverage_report.sh`.

Тесты идут на SQLite в памяти с включёнными внешними ключами. `.env` и работающий RustFS им не нужны: тестовые значения и подмену S3-клиента предоставляет `tests/conftest.py`. Каждый тестовый клиент использует `create_app` с отдельным контейнером и переопределённым провайдером БД. Контракт API сравнивается с `docs/openapi.json`, а определения таблиц и индексов PostgreSQL — с сохранённым снимком. Проверяются также границы слоёв, откаты транзакций, общая сессия запроса, дробные timestamp, epoch zero, календарные повторы и SQL прямой/обратной миграции. На виртуальную машину тесты не выкладываются.

## Локальный запуск через Docker Compose

Из корня репозитория, при запущенном Docker с Compose:

```bash
docker compose -f compose.local.yaml up --build -d --wait
```

Указывайте только `-f compose.local.yaml` во всех локальных командах. Обычный
`docker compose up` выбирает production-файл `docker-compose.yaml` и требует
`DOMAIN`, `BACKEND_IMAGE` и другие переменные деплоя. Локальный файл самостоятельный:
не объединяйте его с production-файлом через два аргумента `-f`.

Compose собирает backend и frontend из текущего кода, запускает PostgreSQL, RustFS
и Caddy. `rustfs-init` создаёт приватный bucket `media` и пользователя приложения,
backend применяет миграции. Переменные CI и файл `.env` для запуска не нужны.
Приложение получает настройки через окружение контейнера, в Python ничего не загружается из файлов.

| Адрес | Что открывает |
|---|---|
| `http://localhost:8080` | Приложение |
| `http://localhost:8080/docs` | Swagger: загрузка фото, генерация и выбор аватара |
| `http://localhost:9001` | Консоль RustFS |
| `http://localhost:9000` | S3 API RustFS для внешних инструментов |

Вход в консоль RustFS: `petcare-local-admin` / `petcare-local-admin-secret`.
Это отдельный проект Compose `petcare-local` с собственными Docker volumes и
локальными тестовыми учётными данными. Все опубликованные порты привязаны к `127.0.0.1`.
Открывайте приложение именно через `localhost`, чтобы Host совпадал с подписанными ссылками.

Для генерации аватаров перед запуском экспортируйте `LLM_PROXY_API_KEY` в окружение
терминала. `LLM_PROXY_URL`, `LLM_AVATAR_MODEL`, `LLM_IMAGE_TOOL_MODEL` и
`LLM_AVATAR_TIMEOUT` также можно переопределить. Без ключа можно проверять загрузку,
просмотр и удаление фото; генерация возвращает `503 AVATAR_GENERATION_UNAVAILABLE`.
После изменения ключа повторите команду запуска, чтобы обновить окружение backend.

Если порт 8080 занят, запустите `LOCAL_PORT=8081 docker compose -f compose.local.yaml up --build -d --wait`.
Адрес приложения и origin подписанных ссылок будут `http://localhost:8081`.
Ссылки по умолчанию действуют 7 дней (`S3_PRESIGNED_TTL=604800`).

```bash
docker compose -f compose.local.yaml logs -f backend rustfs-init
docker compose -f compose.local.yaml down
```

Обычный `down` сохраняет базу и фотографии. Для полного сброса локальных данных:
`docker compose -f compose.local.yaml down -v`.

## Docker и деплой

Из корня репозитория образ собирается командой `docker build -t petcare-backend backend`.
Контейнер применяет миграции перед запуском API на порту `8000`. Проверка готовности —
`/health/readiness`.

Корневой `docker-compose.yaml` запускает PostgreSQL, RustFS, backend, frontend и Caddy.
В корневом `.env` задайте `DOMAIN`, `FRONTEND_IMAGE`, `BACKEND_IMAGE`, `DB_PASSWORD`
и `APP_SECURITY_JWT_SECRET`, а также четыре переменные RustFS ниже (см. `.env.example`),
затем выполните `docker compose up -d`.
Для CI/CD добавьте `DB_PASSWORD`, `APP_SECURITY_JWT_SECRET` и четыре переменные RustFS,
описанные ниже, в защищённые переменные GitLab.
Данные PostgreSQL и RustFS хранятся в отдельных Docker volumes.

### Фотографии: RustFS и подписанные ссылки

Production Compose запускает `rustfs/rustfs:1.0.2` и одноразовый сервис `rustfs-init`.
Перед запуском backend инициализатор создаёт приватный bucket `media`,
отдельного пользователя приложения и политику, разрешающую только чтение,
запись и удаление объектов `media/pets/*`. Повторный запуск безопасен;
при изменении секрета пользователя инициализатор обновляет его.

В корневом `.env` или защищённых переменных GitLab задайте:

| Переменная | Значение |
|---|---|
| `RUSTFS_ROOT_ACCESS_KEY` | Имя администратора хранилища, например `petcare-root` |
| `RUSTFS_ROOT_SECRET_KEY` | Случайный секрет администратора |
| `PHOTOS_ACCESS_KEY` | Другое имя пользователя, например `petcare-photos-app` |
| `PHOTOS_SECRET_KEY` | Отдельный случайный секрет приложения |

Для каждого секрета можно использовать `openssl rand -hex 24`. Не используйте
тестовые или стандартные учётные данные. Только RustFS и инициализатор получают
секрет администратора; backend получает ограниченные учётные данные приложения.

Браузер загружает фото напрямую: `POST /api/v1/pets/{petId}/photo/upload-url`, затем `PUT` на выданную ссылку и `POST .../photo/confirm`. Ключ — `pets/<petId>/photo/<uuid>.<extension>`.
`PUT /api/v1/pets/{petId}/photo` остаётся запасным путём через backend: тот проверяет владельца, тип MIME и ограничение 5 МиБ, загружает объект через
внутренний адрес `http://rustfs:9000` и сохраняет ключ `pets/<uuid>.<extension>`. Сгенерированный аватар хранится в том же bucket,
его ключ — в `generated_avatar_key`. Миграция `0008_pet_avatars` переименовывает
`photo_url` в `photo_key`, сохраняя ключи S3, и добавляет поля аватара.

При чтении или изменении питомца `PhotosGateway` генерирует свежий подписанный
GET URL в `photoUrl` и `generatedAvatarUrl`, например `https://<DOMAIN>/media/pets/<uuid>.png?...`.
`avatarUrl` содержит подписанную ссылку на выбранную картинку.
Ссылка действует 7 дней (`S3_PRESIGNED_TTL=604800`); для обновления ссылки нужно
заново получить питомца. Любой обладатель ссылки может читать объект до её
истечения или удаления объекта. Подписанные ссылки не сохраняются в БД.

Caddy направляет `/media/*` в RustFS, сохраняя Host, путь и query string.
Не добавляйте и не удаляйте префикс пути: `media` — имя bucket.
Дополнительный домен и CORS не нужны. Порты 9000/9001 не публикуются, консоль RustFS
отключена. Доступ к административному API извне не проксируется.

Для запуска используйте обычный `docker compose up -d`. После изменения Caddyfile
на работающем сервере выполните
`docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile`.
Pipeline выполняет `docker compose pull`, затем
`docker compose up -d --force-recreate --wait --wait-timeout 300`.
Контейнеры пересоздаются с сохранением именованных volumes; Caddy читает конфигурацию
при старте. Pipeline ожидает готовности сервисов, отдельная перезагрузка Caddy не нужна.
Необязательные настройки приложения, БД, логов и S3 также можно задать в GitLab CI:
pipeline передаёт их Compose, а Compose — в окружение контейнеров. Файл `.env`
на сервере используется только Docker Compose для подстановки переменных;
Python-приложение его не читает.

В разработке также нужен RustFS. Настройте переменные `S3_*` из `backend/.env.example`
и создайте bucket и пользователя приложения перед загрузкой фотографий.

| Переменная | Назначение | Значение в production |
|---|---|---|
| `S3_ENDPOINT_URL` | Внутренний origin S3 API для загрузки, удаления и инициализации хранилища | `http://rustfs:9000` |
| `S3_PUBLIC_ENDPOINT_URL` | Доступный браузеру origin, используемый при подписи ссылок; без `/media` и других путей | `https://<DOMAIN>` |
| `S3_BUCKET` | Приватный bucket; его имя становится первым компонентом пути URL | `media` |
| `S3_REGION` | Регион для подписи запросов; должен совпадать с конфигурацией RustFS | `us-east-1` |
| `S3_ACCESS_KEY` | Идентификатор ограниченного пользователя приложения | Из `PHOTOS_ACCESS_KEY` |
| `S3_SECRET_KEY` | Секрет пользователя приложения для запросов к S3 и подписи ссылок | Из `PHOTOS_SECRET_KEY` |
| `S3_PRESIGNED_TTL` | Срок действия ссылки в секундах; не срок хранения фотографии | `604800` (7 дней) |
| `S3_UPLOAD_TTL` | Срок подписанной ссылки на прямую загрузку, секунды | `900` (15 минут) |

Compose передаёт эти переменные backend и инициализатору. В корневом `.env` и GitLab
учётные данные по-прежнему задаются как `PHOTOS_ACCESS_KEY` и `PHOTOS_SECRET_KEY`;
Compose преобразует их в `S3_ACCESS_KEY` и `S3_SECRET_KEY` внутри контейнеров.

Путь `/media/pets/...` обслуживает RustFS по подписанным ссылкам; локального
хранения и fallback нет. Старые локальные фотографии автоматически в RustFS
не переносятся: до перехода нужно перенести их в bucket `media` и заменить
значения `photo_url` в БД ключами `pets/<uuid>.<extension>`. Если фотографии уже
есть в bucket `petcare-photos`, скопируйте их в `media` с теми же ключами;
ключи `pets/...` в БД при этом менять не нужно.

Это один узел RustFS: настройте резервное копирование `rustfs_data` и PostgreSQL
на другой сервер и проверяйте восстановление. Docker volume сохраняет данные
при замене контейнера, но не обеспечивает отказоустойчивость сервера.
