# Деплой PetCare

Стенд — один сервер с Docker Compose за Caddy. Пайплайн GitLab собирает образы и выкатывает их из `main`.

| Файл | Что это |
|---|---|
| [`../docker-compose.yaml`](../docker-compose.yaml) | Продакшен: caddy, frontend, backend, postgres, rustfs, rustfs-init |
| [`../compose.local.yaml`](../compose.local.yaml) | Тот же стенд локально, образы собираются из исходников |
| [`Caddyfile`](Caddyfile) | TLS и маршрутизация |
| [`../.gitlab-ci.yml`](../.gitlab-ci.yml) | lint → test → build → deploy |
| [`../.env.example`](../.env.example) | Переменные стенда |

## Маршруты Caddy

| Путь | Куда |
|---|---|
| `/api/*`, `/docs`, `/openapi.json` | backend `:8000` |
| `/media/*` | RustFS `:9000`: фото по подписанным ссылкам, тот же домен, без CORS |
| всё остальное | frontend `:3000` |

## Локально

```bash
docker compose -f compose.local.yaml up --build -d --wait
docker compose -f compose.local.yaml logs -f backend
docker compose -f compose.local.yaml down        # -v — удалить базу и фото
```

| Адрес | Что |
|---|---|
| http://localhost:8080 | Приложение, Swagger на `/docs` |
| http://localhost:9001 | Консоль RustFS (`petcare-local-admin` / `petcare-local-admin-secret`) |

`.env` и переменные CI не нужны. Если порт занят: `LOCAL_PORT=8081 docker compose -f compose.local.yaml up --build -d --wait`. Для генерации аватаров экспортируйте `LLM_PROXY_API_KEY` перед запуском. Не запускайте локально голый `docker compose up`: он берёт продакшен-файл.

## Продакшен

Задача `deploy-production` запускается только из `main`: собирает `.env` из переменных GitLab, копирует на ВМ `docker-compose.yaml`, `Caddyfile` и `.env`, затем выполняет `docker compose pull` и `docker compose up -d --force-recreate --wait`. Backend при старте применяет миграции (`alembic upgrade head`); если миграция упала, API не стартует и healthcheck это покажет. Данные лежат в томах `postgres_data`, `rustfs_data`, `caddy_data` и переживают пересоздание контейнеров.

### Переменные GitLab CI

Обязательные (защищённые):

| Переменная | Значение |
|---|---|
| `DOMAIN` | Домен стенда |
| `DB_PASSWORD` | Пароль PostgreSQL |
| `APP_SECURITY_JWT_SECRET` | Секрет подписи JWT, 32+ случайных символа |
| `RUSTFS_ROOT_ACCESS_KEY`, `RUSTFS_ROOT_SECRET_KEY` | Администратор хранилища; видят только RustFS и `rustfs-init` |
| `PHOTOS_ACCESS_KEY`, `PHOTOS_SECRET_KEY` | Отдельный пользователь приложения с доступом только к `media/pets/*` |

Секреты можно сгенерировать командой `openssl rand -hex 24`.

Необязательные. Если не заданы, действуют значения по умолчанию:

| Переменная | Что включает |
|---|---|
| `ADMIN_LOGIN`, `ADMIN_PASSWORD`, `ADMIN_FULL_NAME` | Админ, создаётся миграцией. По умолчанию `admin` / `admin12345`, как у кнопки быстрого входа; при смене поправьте `frontend/src/shared/config/demo-users.ts` |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` | Web Push. Ключи: `uv run python scripts/generate_vapid_keys.py` в `backend/`. Без них Web Push выключен (`webPushAvailable=false`), остальное работает |
| `NOTIFICATIONS_*`, `WEB_PUSH_ALLOWED_HOSTS`, `WEB_PUSH_TIMEOUT` | Интервал рассылки, допустимые push-службы, таймаут |
| `LLM_PROXY_API_KEY` (+ `LLM_PROXY_URL`, `LLM_AVATAR_MODEL`, `LLM_IMAGE_TOOL_MODEL`, `LLM_AVATAR_TIMEOUT`) | Генерация аватара через Spirit LLM Proxy. Без ключа — `503 AVATAR_GENERATION_UNAVAILABLE`, загрузка фото работает |
| `S3_*`, `APP_*`, `DB_*`, `LOG_*` | Тонкая настройка, см. [`backend/.env.example`](../backend/.env.example) |

### Фото: RustFS

`rustfs-init` при каждом старте идемпотентно создаёт приватный bucket `media`, пользователя приложения и его политику. Backend получает подписанные ссылки на чтение (`S3_PRESIGNED_TTL`, 7 дней) и на прямую загрузку из браузера (`S3_UPLOAD_TTL`, 15 минут). Консоль и порты RustFS наружу не открыты.

RustFS — один узел: настройте бэкап томов `rustfs_data` и `postgres_data` на другой сервер.

### Полезные команды на ВМ

```bash
docker compose ps
docker compose logs -f backend
docker compose exec postgres psql -U petcare -d petcare
```
