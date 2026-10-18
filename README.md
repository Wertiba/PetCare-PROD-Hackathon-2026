# PetCare

Сервис для владельцев питомцев: карточки животных, карта здоровья, журнал питания, напоминания о процедурах и PDF-отчёт для ветеринара.

## Где что лежит

| Папка | Что внутри |
|---|---|
| [`backend/`](backend/README.md) | API на FastAPI, PostgreSQL, миграции, тесты |
| [`backend/docs/`](backend/docs/) | Документы сдачи: [техническая спецификация](backend/docs/spec.md), [презентация](backend/docs/presentation.pdf), [OpenAPI](backend/docs/openapi.json), [схема БД](backend/docs/db-schema.png), [коллекция Postman](backend/docs/petcare.postman_collection.json) |
| [`frontend/`](frontend/README.md) | Веб-клиент на Next.js |
| [`deploy/`](deploy/README.md) | Стенд: Docker Compose, Caddy, RustFS, CI/CD |

## Быстрый старт

```bash
docker compose -f compose.local.yaml up --build -d --wait
```

Приложение откроется на http://localhost:8080, Swagger — на http://localhost:8080/docs.

Демо-входы есть кнопками на странице входа: `жюри1`…`жюри10` (пароль `qwerty12345`) с готовой историей и админ `admin` / `admin12345`.
