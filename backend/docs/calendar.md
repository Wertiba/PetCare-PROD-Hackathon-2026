# Календарь телефона

`GET /api/v1/events/calendar.ics` отдаёт один файл iCalendar. Пользователь сохраняет его и импортирует в календарь телефона: Google, Apple или любой другой, который открывает `.ics`.

Ответ — текст, не JSON. Схема в [`openapi.json`](openapi.json) описывает только заголовки и код ответа.

## Запрос

```
GET /api/v1/events/calendar.ics?petId=&alarmMinutes=1440
Authorization: Bearer <accessToken>
```

| Параметр | Смысл |
|---|---|
| `petId` | необязательный UUID. Оставляет события одного питомца. Без него — все питомцы пользователя |
| `alarmMinutes` | за сколько минут до события поставить напоминание. По умолчанию `1440` (сутки). От `0` до `10080` (неделя). `0` — без напоминания |

В файл попадают только события со статусом `planned`, включая просроченные. Выполненные, пропущенные и отменённые не попадают. Чужие события не попадают. Сортировка по `schedule` по возрастанию, не больше 1000 записей: если их больше, в файл идут самые поздние.

Пустой список всё равно отвечает `200` и валидным календарём без событий.

## Ответ

`200`

| Заголовок | Значение |
|---|---|
| `Content-Type` | `text/calendar; charset=utf-8` |
| `Content-Disposition` | `attachment; filename="petcare.ics"`. С `petId`: `filename="petcare-<petId>.ics"` |

Каждое событие в файле:

| Поле | Откуда |
|---|---|
| `SUMMARY` | `{имя питомца}: {название события}` |
| `DESCRIPTION` | тип по-русски. Если у события есть описание — пустая строка и оно |
| `CATEGORIES` | тот же русский тип |
| `DTSTART` | `schedule` в UTC, доли секунды отбрасываются |
| `DTEND` | час после начала |
| `UID` | `{id события}@petcare` |
| `RRULE` | правило повтора, см. таблицу. У `period=none` правила нет |
| `VALARM` | `TRIGGER:-PT{alarmMinutes}M`. Нет, если `alarmMinutes=0` |

Тип в файле:

| `type` | Подпись |
|---|---|
| `vaccination` | Прививка |
| `parasite_treatment` | Обработка от паразитов |
| `vet_visit` | Визит к ветеринару |
| `medication` | Лекарство |
| `grooming` | Груминг |
| `other` | Другое |

Повтор:

| `period` | `RRULE` |
|---|---|
| `daily` | `FREQ=DAILY` |
| `weekly` | `FREQ=WEEKLY` |
| `monthly` | `FREQ=MONTHLY` |
| `quarterly` | `FREQ=MONTHLY;INTERVAL=3` |
| `half_year` | `FREQ=MONTHLY;INTERVAL=6` |
| `yearly` | `FREQ=YEARLY` |
| `none` | строки нет |

Пример одного события (строки в файле заканчиваются `\r\n`):

```text
BEGIN:VEVENT
UID:11111111-1111-4111-8111-111111111111@petcare
DTSTAMP:20261101T100000Z
DTSTART:20261101T100000Z
DTEND:20261101T110000Z
SUMMARY:Барсик: Прививка от бешенства
DESCRIPTION:Прививка\n\nНобивак
CATEGORIES:Прививка
RRULE:FREQ=YEARLY
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Барсик: Прививка от бешенства
TRIGGER:-PT1440M
END:VALARM
END:VEVENT
```

## Ошибки

Формат как у остальных методов: `{code, message, traceId, timestamp, path, details?}`.

| Статус | Когда |
|---|---|
| `401 UNAUTHORIZED` | нет или плохой токен |
| `404 NOT_FOUND` | `petId` не существует или принадлежит другому пользователю. Сообщение «Pet not found», как у карточки питомца. Это не `422 PET_NOT_FOUND`: тот код бывает у `petId` в теле запроса |
| `422` | `alarmMinutes` вне `0…10080` или `petId` не UUID. В теле `fieldErrors` |

## Фронт

Файл нельзя разобрать как JSON. Запрос с Bearer, тело сохранить как blob.

```ts
const response = await fetch("/api/v1/events/calendar.ics", {
  headers: { Authorization: `Bearer ${accessToken}` },
});
const blob = await response.blob();
const url = URL.createObjectURL(blob);
const link = document.createElement("a");
link.href = url;
link.download = "petcare.ics";
link.click();
URL.revokeObjectURL(url);
```

Имя файла можно взять из `Content-Disposition`, если передан `petId`.

Повторный импорт после новых событий может задвоить повторы. Когда событие отмечают выполненным, сервер создаёт следующее отдельной записью, а старый файл календаря уже содержит `RRULE` на ту же серию. Перед повторным скачиванием лучше сказать пользователю удалить прежний импорт PetCare.
