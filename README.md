# PetCare backend

Бэкенд на FastAPI. В этой ветке готовы регистрация и API питомцев: породы, карточка, фото.

Docker и описание деплоя здесь нет. Их добавляют отдельно, когда сервис выкладывают на виртуальную машину.

## Запуск

Нужен Postgres. Базу `petcare` создайте заранее.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
cp src/.env.example src/.env
```

В `src/.env` пропишите доступ к базе и свой `APP_SECURITY_JWT_SECRET`. Для локального HTTP поставьте `APP_COOKIE_SECURE=false`, иначе браузер не сохранит refresh-cookie.

```bash
cd src
alembic upgrade head
python -m app.run
```

Сервис слушает `http://localhost:8080`. Список методов и схемы запросов: `http://localhost:8080/docs`.

## Авторизация

`POST /api/v1/auth/register` и `POST /api/v1/auth/login` возвращают `accessToken`. Его передают заголовком `Authorization: Bearer <token>`.

Refresh-токен приходит в HttpOnly-cookie `refreshToken`. Обновить access: `POST /api/v1/auth/refresh`. Выйти: `POST /api/v1/auth/logout`.

## Методы

| Метод | Путь | Что делает |
|---|---|---|
| GET | `/health/liveness`, `/health/readiness` | Процесс жив, база отвечает |
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |
| POST | `/api/v1/auth/refresh` | Новый access-токен |
| POST | `/api/v1/auth/logout` | Выход |
| GET | `/api/v1/breeds?type=&q=` | Породы. `type`: `cat` или `dog` |
| GET | `/api/v1/pets` | Свои питомцы |
| POST | `/api/v1/pets` | Создать. Обязательны `name` и `type` |
| GET | `/api/v1/pets/{petId}` | Карточка |
| PATCH | `/api/v1/pets/{petId}` | Изменить переданные поля |
| DELETE | `/api/v1/pets/{petId}` | Удалить |
| PUT | `/api/v1/pets/{petId}/photo` | Фото, поле формы `file`. jpeg, png или webp, до 5 МБ |

Чужой или несуществующий питомец отвечает `404`. Пустое имя и дата рождения в будущем — `422`, в теле есть `fieldErrors`.

Фото отдаётся по пути из `photoUrl`, например `/media/pets/<файл>`. Файлы лежат в `src/media` и в git не попадают.

## Проверка

Из каталога `src`, при заполненном `src/.env`:

```bash
python -m pytest
ruff check .
```

Тесты идут на SQLite в памяти и на виртуальную машину не выкладываются.
