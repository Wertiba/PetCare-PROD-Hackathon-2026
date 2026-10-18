# Аватар питомца

Бэкенд принимает фото, генерирует по нему аватар и отдаёт выбранную картинку. Обе картинки хранятся в приватном RustFS через aioboto3 и `PhotosGateway`; конфигурации и сервисы предоставляет Dishka.

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
Тело необязательно. Без него аватар строится по зашитому стилю. С пожеланием:

```json
{ "prompt": "в красном шарфе" }
```

`prompt` — до 120 символов, только внешний вид: цвет, аксессуар, фон, настроение. Буквы, цифры и знаки `. , ! ? ' - « »`. Просьбы сделать что-то другое (поиск, код, «игнорируй инструкции») не доходят до модели: `422 AVATAR_PROMPT_REJECTED`, поле `prompt`. Пустая строка значит то же, что тела нет.

Ответ может идти до трёх минут: на фронте нужен долгий таймаут и состояние загрузки. `avatarSource` этот метод не меняет.

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
| `422 PHOTO_UPLOAD_NOT_FOUND` | confirm с чужим, несуществующим или не тем ключом |
| `502 AVATAR_GENERATION_FAILED` | Spirit не вернул картинку |
| `503 AVATAR_GENERATION_UNAVAILABLE` | не задан `LLM_PROXY_API_KEY` |
| `422 AVATAR_PROMPT_REJECTED` | `prompt` длиннее 120 символов, с посторонними символами или не про внешний вид |

Ссылки подписанные и живут `S3_PRESIGNED_TTL` секунд (по умолчанию 604800 — 7 дней). Если картинка перестала открываться, карточку питомца нужно запросить заново.

## Прямая загрузка

Браузер кладёт файл сразу в хранилище по подписанной ссылке. Байты через backend не проходят. Пока нет confirm, карточка питомца не меняется.

1. `POST /api/v1/pets/{petId}/photo/upload-url`

```json
{ "contentType": "image/jpeg", "size": 12345 }
```

`contentType` — `image/jpeg`, `image/png` или `image/webp`. `size` — байты, от 1 до 5 МБ. В ответе `key`, `uploadUrl`, `method` (`PUT`), `headers`, `expiresAt` и `maxBytes`.

2. Браузер отправляет файл на `uploadUrl`. `Content-Type` должен совпасть с `headers`: этот заголовок входит в подпись.

```js
await fetch(uploadUrl, { method: "PUT", headers, body: file })
```

Ссылка живёт 15 минут (`S3_UPLOAD_TTL`, по умолчанию 900).

3. `POST /api/v1/pets/{petId}/photo/confirm` с телом `{"key": "<key из шага 1>"}`. В ответе питомец: новое фото, `avatarSource` снова `photo`, старый сгенерированный аватар сброшен.

4. Дальше, как раньше: `POST .../avatar/generate`, затем `PUT .../avatar`.

Пропустить фото или аватар — просто не вызывать эти методы.

`DELETE /api/v1/pets/{petId}/photo` удаляет фото и аватар, собранный из него. `DELETE /api/v1/pets/{petId}/avatar/generated` удаляет только аватар и, если он был выбран, возвращает показ на фото. Повторный вызов ничего не удаляет.

`PUT /api/v1/pets/{petId}/photo` остаётся запасным путём: файл идёт через backend.

В production загрузка идёт на тот же домен (`https://<DOMAIN>/media/...`), отдельный CORS не нужен. Локально RustFS часто на другом порту: тогда браузеру нужен CORS на хранилище, либо используйте multipart `PUT /photo`.

Неподтверждённые загрузки остаются в bucket как сироты. Очистки пока нет.

## Фронт

1. Форма загрузки берёт ссылку из раздела «Прямая загрузка». `PUT .../photo` — запасной путь, не base64.
2. После ответа показывает `photoUrl` и, если есть, `generatedAvatarUrl`.
3. Кнопка «Сделать аватар» вызывает `POST .../avatar/generate` и ждёт ответ.
4. Две кнопки выбора вызывают `PUT .../avatar`.
5. В списках и виджете картинка берётся из `avatarUrl`.

## Что поднять нам

Корневой Compose запускает RustFS и одноразовый сервис `rustfs-init`, который создаёт
приватный bucket `media`, пользователя приложения и политику для `media/pets/*`.
Backend запускается после успешной инициализации. Локального файлового хранилища нет.

В CI задайте четыре переменные хранилища:

```text
RUSTFS_ROOT_ACCESS_KEY=...
RUSTFS_ROOT_SECRET_KEY=...
PHOTOS_ACCESS_KEY=...
PHOTOS_SECRET_KEY=...
```

Compose преобразует `PHOTOS_*` в `S3_ACCESS_KEY` и `S3_SECRET_KEY` для backend.
Администраторские ключи используются только RustFS и инициализатором.
Остальные настройки S3 в production уже имеют значения по умолчанию:

```text
S3_ENDPOINT_URL=http://rustfs:9000
S3_PUBLIC_ENDPOINT_URL=https://<DOMAIN>
S3_REGION=us-east-1
S3_BUCKET=media
S3_PRESIGNED_TTL=604800
S3_UPLOAD_TTL=900
```

`S3_ENDPOINT_URL` — внутренний origin для backend. `S3_PUBLIC_ENDPOINT_URL` — origin,
который открывает браузер, без `/media`: имя bucket добавляется к пути автоматически.
Caddy направляет `/media/*` в RustFS на том же домене приложения.

Для генерации задайте `LLM_PROXY_API_KEY` в защищённых переменных GitLab CI.
Pipeline и Compose передают его backend. Необязательные настройки:

```text
LLM_PROXY_URL=https://llm-proxy.spirit.t-education.com
LLM_AVATAR_MODEL=openai/gpt-5.6-sol
LLM_IMAGE_TOOL_MODEL=gpt-image-1.5
LLM_AVATAR_TIMEOUT=180
```

Ключ LLM берётся в Spirit: тенант → AI → LLM → аккаунт → ключ. Это не пароль GitLab.
У аккаунта должна быть квота на `openai/gpt-5.6-sol`. Без ключа API возвращает
`503 AVATAR_GENERATION_UNAVAILABLE`; загрузка фото и выбор уже созданного аватара работают.

Перед запуском: `alembic upgrade head` (production-контейнер выполняет это автоматически).
Миграция `0008_pet_avatars` переименовывает `photo_url` в `photo_key`, сохраняет ключи
существующих S3-объектов и добавляет поля аватара.

При запуске без Compose экспортируйте `S3_*` и `LLM_*` из `backend/.env.example`
в окружение процесса. Python не читает `.env` и не использует dotenv.
