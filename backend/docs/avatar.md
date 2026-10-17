# Аватар питомца

Бэкенд на ветке `backend/pet-avatar` уже умеет принять фото, нарисовать по нему аватар и отдать выбранную картинку. Фронт и окружение деплоя ещё нужно подключить.

## Что делает пользователь

1. Загружает фото питомца.
2. Может попросить стилизованный аватар. Его рисуют по этому фото, не из текста.
3. Выбирает, что показывать: загруженное фото или аватар.

Пока выбор не сделан, показывается фото. Новая загрузка фото удаляет старый аватар и снова ставит показ на фото.

## API

Все методы требуют авторизацию. Чужой питомец — `404`.

`PUT /api/v1/pets/{petId}/photo`  
`multipart/form-data`, поле `file`. jpeg, png или webp, до 5 МБ.

`POST /api/v1/pets/{petId}/avatar/generate`  
Тела нет. Ответ может идти до трёх минут: на фронте нужен долгий таймаут и состояние загрузки. `avatarSource` этот метод не меняет.

`PUT /api/v1/pets/{petId}/avatar`

```json
{ "source": "photo" }
```

или `"generated"`.

В карточке питомца (`GET /api/v1/pets` и `GET /api/v1/pets/{petId}`):

| Поле | Смысл |
|---|---|
| `photoUrl` | оригинал или `null` |
| `generatedAvatarUrl` | аватар или `null` |
| `avatarSource` | `photo` или `generated` |
| `avatarUrl` | что показывать в интерфейсе |

Ошибки:

| Код | Когда |
|---|---|
| `422 PET_PHOTO_REQUIRED` | генерация или выбор фото, а фото нет |
| `422 GENERATED_AVATAR_MISSING` | выбрали аватар, а его ещё не генерировали |
| `413` | файл больше 5 МБ |
| `415` | не jpeg/png/webp |
| `502 AVATAR_GENERATION_FAILED` | Spirit не вернул картинку |
| `503 AVATAR_GENERATION_UNAVAILABLE` | не задан `LLM_PROXY_API_KEY` |

На S3 ссылки подписанные и живут `S3_PRESIGN_EXPIRES` секунд (по умолчанию час). Если картинка перестала открываться, карточку питомца нужно запросить заново.

## Фронт

1. Форма загрузки шлёт файл на `PUT .../photo`, не base64.
2. После ответа показывает `photoUrl` и, если есть, `generatedAvatarUrl`.
3. Кнопка «Сделать аватар» вызывает `POST .../avatar/generate` и ждёт ответ.
4. Две кнопки выбора вызывают `PUT .../avatar`.
5. В списках и виджете картинка берётся из `avatarUrl`.

## Что поднять нам

Spirit бакет не выдаёт. Нужен свой S3-совместимый сервис (MinIO или другой) и бакет, например `petcare`. Бэкенд бакет сам не создаёт.

В окружение процесса backend, не в репозиторий:

```
APP_STORAGE_BACKEND=s3
S3_ENDPOINT_URL=http://minio:9000
S3_PUBLIC_ENDPOINT_URL=https://storage.example
S3_REGION=us-east-1
S3_BUCKET=petcare
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_PRESIGN_EXPIRES=3600

LLM_PROXY_URL=https://llm-proxy.spirit.t-education.com
LLM_PROXY_API_KEY=...
LLM_AVATAR_MODEL=openai/gpt-5.6-sol
LLM_IMAGE_TOOL_MODEL=gpt-image-1.5
LLM_AVATAR_TIMEOUT=180
```

`S3_ENDPOINT_URL` — адрес, с которого ходит backend. `S3_PUBLIC_ENDPOINT_URL` — адрес, который открывает браузер. Если они совпадают, второй можно не задавать.

Ключ LLM берётся в Spirit: тенант → AI → LLM → аккаунт → ключ. Это не пароль GitLab. У аккаунта должна быть квота на `openai/gpt-5.6-sol`.

Корневой `docker-compose.yaml` эти переменные пока не передаёт в сервис `backend`. Их нужно добавить в окружение сервиса и в защищённые переменные GitLab. Том `backend_media` при `s3` не используется.

Перед запуском: `alembic upgrade head`. Миграция `0008_pet_avatars` переименовывает `photo_url` в `photo_key` и добавляет аватар.

Локально без S3 достаточно `APP_STORAGE_BACKEND=local`: файлы лягут в `backend/media`, ссылки будут вида `/media/pets/...`. Генерация и тогда требует `LLM_PROXY_API_KEY`.
