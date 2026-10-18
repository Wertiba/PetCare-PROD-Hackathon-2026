# PetCare frontend

Веб-клиент PetCare: лендинг, вход и регистрация, дашборд питомца (карта здоровья, питание, календарь напоминаний), личный кабинет и админка справочников.

## Стек

Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, TanStack Query, Zustand, React Hook Form + Zod, Recharts.

## Структура

Код разложен по Feature-Sliced Design:

```text
frontend/
├── app/            # маршруты Next.js: /, /login, /register, /dashboard, /account, /admin
├── src/
│   ├── app/        # провайдеры (сессия, React Query), глобальные стили
│   ├── widgets/    # крупные блоки страниц: дашборд, календарь, админка, лендинг
│   ├── features/   # действия пользователя: вход, создать питомца, записать кормление...
│   ├── entities/   # сущности API: pet, event, food, state, user... (запросы, типы)
│   └── shared/     # API-клиент, конфиг, утилиты
└── public/         # иконки, manifest, service worker для Web Push
```

## API и авторизация

Браузер ходит на тот же origin: Next.js проксирует `/api/v1/*` на бэкенд (`rewrites` в `next.config.ts`, адрес — `BACKEND_ORIGIN`, по умолчанию `http://localhost:8080`). Access- и refresh-токены лежат в httpOnly-cookie, которые ставит бэкенд; фронт их не хранит. При `401` клиент один раз вызывает `/auth/refresh` и повторяет запрос.

Контракт API — [`../backend/docs/openapi.json`](../backend/docs/openapi.json).

## Запуск

```bash
npm ci
npm run dev        # http://localhost:3000, нужен запущенный бэкенд
```

Проще поднять весь стенд из корня репозитория: `docker compose -f compose.local.yaml up --build -d --wait`.

## Проверки

```bash
npm run typecheck
npm run lint
npm run build
```
