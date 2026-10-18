# Внешние напоминания

Бэкенд по-прежнему хранит уведомления и отдаёт `GET /api/v1/notifications?due=true` для тостов в приложении. Поле `status` значит то же, что раньше: фронт сам переводит его в `read`. Отдельное поле `deliveredAt` отмечает, что напоминание уже ушло в Web Push. Пока оно пустое и время наступило, фоновый цикл пытается отправить его.

Пока пользователь не включил Web Push, снаружи ничего не уходит, а список `due=true` работает как раньше.

## Что делает пользователь

1. Открывает настройки уведомлений.
2. Включает Web Push. Сайт запрашивает разрешение и отправляет подписку браузера.
3. Кнопка «Проверить» вызывает `POST /notifications/test` и показывает, ответил ли канал.

## API

Все методы ниже требуют авторизацию. Их пути объявлены раньше `/{notificationId}`, чтобы слово `settings` не считалось идентификатором.

`GET /api/v1/notifications/settings`

```json
{
  "webPushEnabled": false,
  "webPushAvailable": true
}
```

`webPushAvailable` — заданы ли ключи VAPID.

`PATCH /api/v1/notifications/settings` принимает `webPushEnabled`.

| Код | Когда |
|---|---|
| `503 WEB_PUSH_NOT_CONFIGURED` | включают Web Push или просят публичный ключ, а VAPID не задан |

`GET /api/v1/notifications/web-push/public-key` → `{ "publicKey": "<base64url>" }`.

`POST /api/v1/notifications/web-push/subscriptions` — объект `PushSubscription` из браузера:

```json
{
  "endpoint": "https://push.example.com/...",
  "expirationTime": null,
  "keys": { "p256dh": "...", "auth": "..." }
}
```

Повтор с тем же `endpoint` обновляет ключи и владельца. `expirationTime` принимается и не хранится.

`DELETE /api/v1/notifications/web-push/subscriptions` — `endpoint` в query или в JSON. Чужая и отсутствующая подписка не удаляются, ответ всё равно `204`.

`POST /api/v1/notifications/test` сразу шлёт проверку, если Web Push включён:

```json
{
  "channels": [
    { "channel": "web_push", "ok": false, "error": "no_subscriptions" }
  ]
}
```

Пустой `channels` — канал выключен. `no_subscriptions` — Web Push включён, а подписок нет. `not_configured` — ключи VAPID не заданы. `delivery_failed` — служба пуша ответила ошибкой. `subscription_gone` — служба пуша ответила 404 или 410, подписка удалена.

В карточке уведомления добавилось необязательное `deliveredAt`. `status` этот цикл не меняет.

## Фронт

Тосты не трогать: опрос `due=true` и `PATCH` статуса остаются.

Настройки:

1. `GET /notifications/settings`.
2. Если `webPushAvailable` ложь, кнопку Web Push не показывать.
3. Тумблер вызывает `PATCH /notifications/settings` с `webPushEnabled`.

Web Push, в уже зарегистрированном service worker:

1. `GET /notifications/web-push/public-key`.
2. `pushManager.subscribe({ userVisibleOnly: true, applicationServerKey })`. Ключ из ответа — base64url; его нужно перевести в `Uint8Array` перед subscribe.
3. `POST /notifications/web-push/subscriptions` с `subscription.toJSON()`.
4. При выходе или отказе — `DELETE` с тем же `endpoint`.

Service worker на событии `push` читает JSON `{ title, body, notificationId, eventId, petId, url }`. `url` сейчас всегда `"/"`. У проверочного сообщения идентификаторы равны `null`. Показ через `registration.showNotification(title, { body, data })`. По клику открывать `data.url`.

Ответ пуша 404 или 410 значит, что браузер отозвал подписку. Бэкенд удаляет её сам. Имеет смысл подписаться заново при следующем заходе.

## Что происходит на сервере

Раз в `NOTIFICATIONS_DISPATCH_INTERVAL` секунд (по умолчанию 15) выбираются записи со `status=pending`, временем не позже текущего и не старше `NOTIFICATIONS_MAX_LATENESS` секунд (по умолчанию сутки), у которых пустой `deliveredAt`. Каждая атомарно помечается `deliveredAt=now` условием `delivered_at IS NULL`. Второй процесс видит, что строка уже занята, и не шлёт её снова. Ошибка одной подписки или одной записи пишется в лог и не останавливает цикл. Рассылка может работать на каждом процессе: захват строки не даёт послать дважды.

Web Push получает `title` «Напоминание: <событие>», `body` с именем питомца и временем в UTC, плюс идентификаторы и `url`.

Ключи VAPID:

```bash
uv run python scripts/generate_vapid_keys.py
```

В окружение процесса (файл `.env` приложение не читает):

```text
NOTIFICATIONS_WORKER_ENABLED=true
NOTIFICATIONS_DISPATCH_INTERVAL=15
NOTIFICATIONS_MAX_LATENESS=86400
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_SUBJECT=mailto:admin@example.com
```

Без VAPID методы Web Push отвечают `503`, настройки открываются с `webPushAvailable=false`. Перед запуском: `alembic upgrade head`. Миграция `0010_notification_delivery` добавляет `delivered_at`, таблицу настроек и таблицу подписок.
