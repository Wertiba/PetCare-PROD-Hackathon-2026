# Изменения API для фронта

Новые записи добавляются сверху. Полная схема API: [`openapi.json`](openapi.json).

## 2026-10-17 · аккаунты жюри

- **Миграция `0007` создаёт аккаунты `жюри1`…`жюри10`** с паролем `qwerty12345`, ровно как в `demo-users.ts`. Кнопки быстрого входа теперь работают на любом окружении, где выполнен `alembic upgrade head`.

## 2026-10-17 · fix: ошибка неверного логина

- **Неверный логин или пароль** в `POST /auth/login` теперь отвечает `401 WRONG_LOGIN_OR_PASSWORD` с сообщением «Wrong login or password». Раньше было `401 UNAUTHORIZED` «The token is missing or invalid».
- **Плохой или просроченный токен** по-прежнему отвечает `401 UNAUTHORIZED`.

## 2026-10-17 · `backend/admin_crud`

### Что поменять
- **Питомец, создание:** `type` больше не передаётся, `breedId` теперь обязателен.
  `POST /pets {name, breedId, birthDate?}`
- **Питомец, ответ:** вместо `type` приходят объекты `animal {id, name}` и `breed {id, name}`. Оба равны `null`, только если админ удалил породу.
- **Питомец, PATCH:** вид меняется через `breedId` породы другого вида. `breedId: null` даёт 422.
- **Породы:** фильтр `?type=cat` заменён на `?animalId=<uuid>`. В ответе вместо `type` теперь `animalId`.
- **Категории** общие для всех пользователей. Кнопки «изменить» и «удалить» показывать, только если `createdBy === me.id` или `me.role === "ADMIN"`.
- **Удалено:** `pets.type` из `enums.json` и код ошибки `BREED_TYPE_MISMATCH`.

### Регистрация питомца
1. Виды: `GET /animals`.
2. Породы выбранного вида: `GET /breeds?animalId=`.
3. Создание: `POST /pets`.

### Новое
| Эндпоинт | Зачем |
|---|---|
| `GET /animals?q=`, `GET /animals/{id}` | список видов |
| `POST/PATCH/DELETE /animals`, `/breeds` | админка: только для `role === "ADMIN"` |
| `/notes?petId=&q=` + CRUD | заметки в карточке питомца `{petId, content}` |
| `/foods?petId=&isApproach=&isTolerability=` + CRUD | журнал кормления |
| `GET /foods/{id}/suspects` | ингредиенты, которых не было в ранее подошедших кормах |

Тело запроса на кормление (`POST /foods`):
```json
{ "petId": "…", "name": "Royal Canin", "weight": 50, "ingredients": ["Курица", "Рис"],
  "isApproach": true, "isTolerability": null, "consequences": null }
```
- `isApproach`: понравилось. `isTolerability`: подошло. `null` означает «ещё не оценили», можно дозаполнить позже через PATCH.
- Ответ `/suspects`: `{suspects: [...], comparedFoods: N}`. Если `comparedFoods = 0`, подозрительными будут все ингредиенты. В этом случае стоит показать подсказку «отмечайте подошедшие корма».

### Новые ошибки
- `403 FORBIDDEN`: не админ меняет виды или породы, либо не автор меняет категорию.
- `409 CATEGORY_IN_USE`: нельзя удалить категорию или сменить ей `kind`/`type`, пока ей пользуются другие.
- `409 CONFLICT`: дубликат имени вида или породы.
- `422 ANIMAL_NOT_FOUND`: неизвестный `animalId`.
