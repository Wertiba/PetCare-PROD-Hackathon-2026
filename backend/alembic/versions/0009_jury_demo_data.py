"""demo history for the jury accounts: every жюри gets its own pets with vaccinations, treatments, vet visits,
medications, weight and appetite measurements, a food journal, notes and reminders

Dates are counted back from the moment the migration runs, so each account opens with overdue procedures,
something due this week and a year of history behind it.

Revision ID: 0009_jury_demo_data
Revises: 0008_states_category_id
"""

import json
import random
import uuid
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import time

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0009_jury_demo_data"
down_revision = "0008_states_category_id"
branch_labels = None
depends_on = None

DAY = 86400.0
_JURY_COUNT = 10

# Breed ids seeded by 0002 (cats 1.., dogs 101..) and 0006 (fish 201..); category ids seeded by 0003.
_BREEDS = {
    "british": 1, "maine_coon": 2, "sphynx": 7, "siberian": 15, "cat_mix": 16,
    "labrador": 101, "shepherd": 102, "spitz": 103, "corgi": 109, "pug": 115, "dog_mix": 116,
    "goldfish": 201, "betta": 203,
}  # fmt: skip
_CATEGORIES = {"weight": 1, "water": 3, "walk": 4, "activity": 5, "appetite": 6, "gi": 10, "allergy": 11}
_PERIOD_DAYS = {"weekly": 7, "monthly": 30, "quarterly": 91, "half_year": 182, "yearly": 365}


def _jury_id(number: int) -> uuid.UUID:
    """Same ids as 0007_jury_users."""
    return uuid.UUID(f"00000000-0000-4000-b000-{number:012d}")


def _breed_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-8000-{number:012d}")


def _category_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-9000-{number:012d}")


@dataclass(frozen=True)
class Procedure:
    """A repeating procedure: past occurrences are done, the next one is planned (or already overdue)."""

    name: str
    type: str
    period: str
    next_in_days: float  # negative: overdue
    done_times: int
    description: str | None = None


@dataclass(frozen=True)
class Visit:
    name: str
    days_ago: float
    conclusion: str


@dataclass(frozen=True)
class Feeding:
    name: str
    ingredients: tuple[str, ...]
    liked: bool | None
    suited: bool | None
    reaction: str | None = None
    times: int = 1


@dataclass(frozen=True)
class PetTemplate:
    name: str
    breed: str
    age_days: int
    weight_from: int  # grams, a year ago or at the earliest measurement
    weight_to: int
    procedures: tuple[Procedure, ...]
    visits: tuple[Visit, ...] = ()
    feedings: tuple[Feeding, ...] = ()
    notes: tuple[str, ...] = ()
    scales: tuple[str, ...] = ("appetite", "activity")
    walks: bool = False
    water: bool = False
    reactions: tuple[str, ...] = ()  # "gi" / "allergy" check measurements
    extra: dict = field(default_factory=dict)


_CHICKEN = Feeding("Royal Canin Indoor", ("Курица", "Рис", "Кукуруза"), True, True, times=6)
_TURKEY = Feeding("Grandorf индейка", ("Индейка", "Рис", "Льняное семя"), True, True, times=4)
_SALMON = Feeding(
    "Monge лосось с горохом", ("Лосось", "Горох", "Рис"), False, False, "Зуд и покраснение кожи через 2 часа", 2
)
_BEEF = Feeding("Влажный корм с говядиной", ("Говядина", "Морковь"), True, False, "Мягкий стул, вздутие", 2)
_LAMB = Feeding("Acana ягнёнок", ("Ягнёнок", "Овёс", "Тыква"), True, True, times=5)
_DUCK = Feeding("Brit утка и картофель", ("Утка", "Картофель"), False, True, times=3)
_FLAKES = Feeding("Tetra хлопья", ("Рыбная мука", "Спирулина"), True, True, times=8)
_BLOODWORM = Feeding("Мотыль замороженный", ("Мотыль",), True, False, "Вздутие, отказ от еды на сутки", 2)

_TEMPLATES = (
    PetTemplate(
        "Барсик", "british", 4 * 365 + 40, 4300, 4900,
        (
            Procedure("Комплексная вакцина (Нобивак Tricat)", "vaccination", "yearly", 24, 3),
            Procedure("Вакцина от бешенства", "vaccination", "yearly", -6, 3),
            Procedure("Капли от блох и клещей (Стронгхолд)", "parasite_treatment", "quarterly", 9, 4),
            Procedure("Дегельминтизация (Мильбемакс)", "parasite_treatment", "quarterly", 40, 4),
        ),
        (
            Visit("Плановый осмотр", 150, "Здоров. Лёгкий избыток веса: +300 г к норме. Рекомендована диета и игры."),
            Visit("Чистка зубов", 60, "Удалён зубной камень. Повторный осмотр через год."),
        ),
        (_CHICKEN, _SALMON, _TURKEY),
        ("Не любит переноску — заманивать лакомством", "Аллергия на рыбу, лосось исключить"),
        reactions=("allergy",),
    ),
    PetTemplate(
        "Рекс", "shepherd", 6 * 365, 36500, 34800,
        (
            Procedure("Комплексная вакцина (Нобивак DHPPi+L)", "vaccination", "yearly", 75, 5),
            Procedure("Вакцина от бешенства", "vaccination", "yearly", 75, 5),
            Procedure("Таблетка от клещей (Бравекто)", "parasite_treatment", "quarterly", -2, 4),
            Procedure("Хондропротектор (Артроглюкан)", "medication", "daily", 0.4, 20, "1 таблетка утром с едой"),
        ),
        (
            Visit("Ортопед", 45, "Начальная дисплазия тазобедренных суставов. Хондропротектор курсом 2 месяца, "
                  "умеренные нагрузки, контроль веса."),
            Visit("Плановый осмотр", 200, "Здоров. Рекомендовано снизить вес на 1–2 кг."),
        ),
        (_LAMB, _BEEF),
        ("Боится салютов — в новогоднюю ночь не выгуливать",),
        scales=("appetite", "activity"), walks=True, reactions=("gi",),
    ),
    PetTemplate(
        "Мурка", "maine_coon", 210, 1600, 4100,
        (
            Procedure("Вакцина Нобивак Tricat — 2-я прививка", "vaccination", "yearly", 5, 1),
            Procedure("Вакцина от бешенства", "vaccination", "yearly", 21, 0),
            Procedure("Дегельминтизация (Празицид)", "parasite_treatment", "monthly", 3, 5),
        ),
        (Visit("Первичный осмотр котёнка", 150, "Здорова. График прививок составлен, кастрация после 8 месяцев."),),
        (Feeding("Royal Canin Kitten", ("Курица", "Рис", "Яичный порошок"), True, True, times=8), _BEEF),
        ("Котёнок, растёт: взвешивать каждый месяц",),
    ),
    PetTemplate(
        "Голди", "goldfish", 2 * 365, 0, 0,
        (
            Procedure("Подмена 30% воды", "other", "weekly", 1, 30),
            Procedure("Чистка фильтра", "other", "monthly", -1, 10),
            Procedure("Тест воды (pH, нитраты)", "other", "monthly", 12, 10),
        ),
        (),
        (_FLAKES, _BLOODWORM),
        ("Аквариум 60 л, температура 22–24 °C",),
        scales=("activity",), water=False,
    ),
    PetTemplate(
        "Тоша", "corgi", 2 * 365 + 100, 10800, 12400,
        (
            Procedure("Комплексная вакцина (Эурикан DHPPi2-LR)", "vaccination", "yearly", 130, 2),
            Procedure("Таблетка от блох и клещей (Симпарика)", "parasite_treatment", "monthly", 4, 10),
            Procedure("Груминг: вычёсывание и стрижка когтей", "grooming", "monthly", -3, 8),
        ),
        (Visit("Плановый осмотр", 90, "Здоров. Вес на верхней границе нормы — сократить лакомства."),),
        (_CHICKEN, _DUCK, _BEEF),
        ("Обожает морковку как лакомство",),
        walks=True, reactions=("gi",),
    ),
    PetTemplate(
        "Луна", "sphynx", 3 * 365, 3000, 3200,
        (
            Procedure("Комплексная вакцина (Пуревакс)", "vaccination", "yearly", 200, 3),
            Procedure("Купание и уход за кожей", "grooming", "weekly", 2, 40),
            Procedure("Антигистаминный курс", "medication", "daily", 0.3, 12, "Супрастин ¼ таблетки вечером"),
        ),
        (
            Visit("Дерматолог", 30, "Пищевая аллергия. Гипоаллергенная диета 8 недель, антигистаминное 14 дней."),
        ),
        (_SALMON, Feeding("Hill's z/d гипоаллергенный", ("Гидролизат курицы", "Крахмал"), True, True, times=6)),
        ("Мёрзнет — зимой нужен свитер",),
        reactions=("allergy",),
    ),
    PetTemplate(
        "Бублик", "pug", 5 * 365, 10500, 9200,
        (
            Procedure("Комплексная вакцина (Нобивак DHPPi+L)", "vaccination", "yearly", -12, 4),
            Procedure("Таблетка от клещей (Некс Гард)", "parasite_treatment", "monthly", 6, 10),
            Procedure("Чистка складок на морде", "grooming", "weekly", 1, 30),
        ),
        (
            Visit("Диетолог", 120, "Ожирение I степени. Диета 900 ккал/сутки, цель — 9 кг за 4 месяца."),
            Visit("Контроль веса", 20, "Минус 1,3 кг. Диету продолжать."),
        ),
        (Feeding("Royal Canin Satiety", ("Птица", "Клетчатка", "Рис"), False, True, times=6), _BEEF),
        ("Храпит — норма для породы, но следить за дыханием в жару",),
        walks=True,
    ),
    PetTemplate(
        "Снежок", "siberian", 8 * 365, 6200, 5700,
        (
            Procedure("Комплексная вакцина (Мультифел-4)", "vaccination", "yearly", 33, 7),
            Procedure("Капли от блох (Инспектор)", "parasite_treatment", "quarterly", -9, 6),
            Procedure("Почечная диета: контроль анализов", "vet_visit", "half_year", 50, 2),
        ),
        (
            Visit("Терапевт", 130, "Начальная стадия ХБП. Почечная диета, контроль креатинина раз в полгода."),
        ),
        (Feeding("Royal Canin Renal", ("Рис", "Кукуруза", "Птица"), True, True, times=5), _CHICKEN),
        ("Пожилой кот, пьёт много — следить за водой",),
        water=True, reactions=("gi",),
    ),
    PetTemplate(
        "Джек", "labrador", 365 + 60, 22000, 30500,
        (
            Procedure("Комплексная вакцина (Эурикан)", "vaccination", "yearly", 60, 1),
            Procedure("Вакцина от бешенства", "vaccination", "yearly", 60, 1),
            Procedure("Таблетка от клещей (Бравекто)", "parasite_treatment", "quarterly", 15, 3),
            Procedure("Дегельминтизация (Дронтал)", "parasite_treatment", "quarterly", -4, 3),
        ),
        (Visit("Осмотр молодой собаки", 100, "Здоров, развитие по возрасту. Кастрация — после 18 месяцев."),),
        (_LAMB, _TURKEY, _SALMON),
        ("Ест всё подряд на прогулке — нужен намордник",),
        walks=True,
    ),
    PetTemplate(
        "Пушок", "spitz", 4 * 365, 2900, 3100,
        (
            Procedure("Комплексная вакцина (Нобивак DHPPi+L)", "vaccination", "yearly", 2, 3),
            Procedure("Таблетка от блох и клещей (Симпарика)", "parasite_treatment", "monthly", 18, 12),
            Procedure("Груминг: стрижка", "grooming", "quarterly", 25, 4),
        ),
        (Visit("Стоматолог", 75, "Удалены 2 молочных зуба, остальное в норме."),),
        (_DUCK, _CHICKEN),
        (),
        walks=True,
    ),
    PetTemplate(
        "Рыжик", "cat_mix", 1 * 365 + 200, 3200, 4200,
        (
            Procedure("Комплексная вакцина (Нобивак Tricat)", "vaccination", "yearly", 140, 1),
            Procedure("Капли от блох (Адвокат)", "parasite_treatment", "monthly", -1, 6),
        ),
        (Visit("Кастрация", 180, "Операция прошла без осложнений. Корм для стерилизованных."),),
        (Feeding("Purina Pro Plan Sterilised", ("Кролик", "Пшеница"), True, True, times=5), _BEEF),
        ("Взят из приюта",),
    ),
    PetTemplate(
        "Ариэль", "betta", 365, 0, 0,
        (
            Procedure("Подмена 20% воды", "other", "weekly", -1, 20),
            Procedure("Профилактика грибка (Антипар)", "medication", "monthly", 9, 3),
        ),
        (),
        (Feeding("Tetra Betta гранулы", ("Рыбная мука", "Креветка"), True, True, times=6),),
        ("Петушок, нельзя подсаживать других самцов",),
        scales=("activity",),
    ),
)  # fmt: skip

# Each account gets a different pair (or trio) of pets; together the ten accounts cover every template.
_ASSIGNMENT = {
    1: (0, 1), 2: (2, 3, 4), 3: (5, 6), 4: (7, 8), 5: (9, 10, 11),
    6: (1, 2), 7: (4, 5), 8: (6, 0, 3), 9: (8, 9), 10: (11, 7, 10),
}  # fmt: skip


def _add_months(moment: float, months: int) -> float:
    original = datetime.fromtimestamp(moment, UTC)
    year, month = divmod(original.year * 12 + original.month - 1 + months, 12)
    month += 1
    return original.replace(year=year, month=month, day=min(original.day, monthrange(year, month)[1])).timestamp()


def _step(moment: float, period: str, times: int) -> float:
    """Move a moment by whole periods: calendar months for month-based ones, like the app does."""
    if period == "daily":
        return moment + times * DAY
    if period == "weekly":
        return moment + times * 7 * DAY
    months = {"monthly": 1, "quarterly": 3, "half_year": 6, "yearly": 12}[period]
    return _add_months(moment, months * times)


def demo_rows(owner_id: uuid.UUID, template_numbers: tuple[int, ...], now: float, seed: int) -> dict[str, list[dict]]:
    """Rows for one owner's pets. Kept pure so tests can load the same history into SQLite."""
    rng = random.Random(seed)
    rows: dict[str, list[dict]] = {"pets": [], "events": [], "notifications": [], "states": [], "food": [], "notes": []}

    def add_state(pet_id: uuid.UUID, category: str, value: int, moment: float, note: str | None = None) -> None:
        rows["states"].append({
            "id": uuid.uuid4(), "pet_id": pet_id, "category_id": _category_id(_CATEGORIES[category]),
            "value": value, "note": note, "time": moment, "created_at": moment,
        })  # fmt: skip

    for template in (_TEMPLATES[number] for number in template_numbers):
        pet_id = uuid.uuid4()
        birth = datetime.fromtimestamp(now - template.age_days * DAY, UTC)
        created = now - min(template.age_days, 3 * 365 + 30) * DAY
        rows["pets"].append({
            "id": pet_id, "user_id": owner_id, "breed_id": _breed_id(_BREEDS[template.breed]), "name": template.name,
            "birth_date": datetime(birth.year, birth.month, birth.day, tzinfo=UTC).timestamp(), "photo_key": None,
            "created_at": created, "updated_at": now,
        })  # fmt: skip

        for procedure in template.procedures:
            # Hours of the day vary so the history does not look machine-made.
            planned = now + procedure.next_in_days * DAY + rng.randint(-3, 3) * 3600
            for back in range(procedure.done_times, 0, -1):
                schedule = _step(planned, procedure.period, -back)
                if schedule < created:
                    continue
                done_at = schedule + rng.choice((0, 0, DAY, 2 * DAY))
                rows["events"].append({
                    "id": uuid.uuid4(), "pet_id": pet_id, "name": procedure.name, "type": procedure.type,
                    "status": "done", "schedule": schedule, "period": procedure.period,
                    "description": procedure.description, "done_at": done_at, "created_at": schedule - 7 * DAY,
                    "updated_at": done_at,
                })  # fmt: skip
            event_id = uuid.uuid4()
            rows["events"].append({
                "id": event_id, "pet_id": pet_id, "name": procedure.name, "type": procedure.type, "status": "planned",
                "schedule": planned, "period": procedure.period, "description": procedure.description,
                "done_at": None, "created_at": now - DAY, "updated_at": now - DAY,
            })  # fmt: skip
            remind_at = planned - (3600 if procedure.period == "daily" else DAY)
            rows["notifications"].append({
                "id": uuid.uuid4(), "event_id": event_id, "type": "app",
                "status": "pending" if remind_at > now - 2 * DAY else "sent", "time": remind_at, "created_at": now - DAY,
            })  # fmt: skip

        for visit in template.visits:
            moment = now - visit.days_ago * DAY
            rows["events"].append({
                "id": uuid.uuid4(), "pet_id": pet_id, "name": visit.name, "type": "vet_visit", "status": "done",
                "schedule": moment, "period": "none", "description": visit.conclusion, "done_at": moment,
                "created_at": moment - 3 * DAY, "updated_at": moment,
            })  # fmt: skip

        if template.weight_to:
            points = 12 if template.age_days > 365 else max(template.age_days // 30, 3)
            for index in range(points + 1):
                share = index / points
                weight = template.weight_from + (template.weight_to - template.weight_from) * share
                noise = rng.uniform(-0.012, 0.012) * weight
                moment = now - (points - index) * 30 * DAY - rng.randint(0, 2) * DAY
                add_state(pet_id, "weight", int(round(weight + noise, -1)), moment)

        for week in range(10):
            moment = now - week * 7 * DAY - rng.randint(0, 2) * DAY
            for scale in template.scales:
                add_state(pet_id, scale, rng.choice((3, 4, 4, 5, 5)), moment)
            if template.walks:
                add_state(pet_id, "walk", rng.randint(70, 140), moment)
            if template.water:
                add_state(pet_id, "water", rng.randint(250, 400), moment)
        for reaction in template.reactions:
            for days_ago in rng.sample(range(5, 120), 2):
                add_state(pet_id, reaction, 1, now - days_ago * DAY)

        # Feedings spread over the last four months in template order: what suited first, then the trials.
        total = sum(feeding.times for feeding in template.feedings)
        index = 0
        for feeding in template.feedings:
            for _ in range(feeding.times):
                moment = now - 120 * DAY * (1 - index / total) + rng.randint(0, 20) * 3600
                index += 1
                portion = (
                    2 if not template.weight_to else 300 if template.weight_to > 20000 else rng.choice((40, 60, 80))
                )
                rows["food"].append({
                    "id": uuid.uuid4(), "pet_id": pet_id, "name": feeding.name, "weight": portion,
                    "ingredients": list(feeding.ingredients), "is_approach": feeding.liked,
                    "is_tolerability": feeding.suited, "consequences": feeding.reaction,
                    "created_at": moment, "updated_at": moment,
                })  # fmt: skip

        for index, content in enumerate(template.notes):
            moment = now - (20 + 45 * index) * DAY
            rows["notes"].append({
                "id": uuid.uuid4(), "pet_id": pet_id, "content": content, "created_at": moment, "updated_at": moment
            })  # fmt: skip
    return rows


class _JsonText(sa.types.TypeDecorator):
    """JSON passed as text and cast in SQL: asyncpg binds it, `alembic upgrade --sql` renders it as a literal."""

    impl = sa.Text
    cache_ok = True

    def bind_expression(self, bindvalue):
        return sa.cast(bindvalue, postgresql.JSONB)


def _table(name: str, *columns: str) -> sa.TableClause:
    types = {
        "id": postgresql.UUID(as_uuid=True), "pet_id": postgresql.UUID(as_uuid=True),
        "user_id": postgresql.UUID(as_uuid=True), "breed_id": postgresql.UUID(as_uuid=True),
        "event_id": postgresql.UUID(as_uuid=True), "category_id": postgresql.UUID(as_uuid=True),
        "ingredients": _JsonText(), "is_approach": sa.Boolean(), "is_tolerability": sa.Boolean(),
        "value": sa.Integer(), "weight": sa.Integer(),
    }  # fmt: skip
    return sa.table(
        name,
        *(sa.column(column, types.get(column, sa.Text() if column in _TEXT else sa.Float())) for column in columns),
    )


_TEXT = {"name", "photo_key", "type", "status", "period", "description", "note", "consequences", "content"}
_ORDER = ("pets", "events", "notifications", "states", "food", "notes")


def upgrade() -> None:
    now = time()
    numbers = list(range(1, _JURY_COUNT + 1))
    if not op.get_context().as_sql:
        # 0007 skips a login that already existed, so seed only the accounts that are really ours.
        found = op.get_bind().execute(
            sa.text("SELECT id FROM users WHERE id = ANY(:ids)"), {"ids": [_jury_id(n) for n in numbers]}
        )
        existing = {row[0] for row in found}
        numbers = [number for number in numbers if _jury_id(number) in existing]
    tables: dict[str, list[dict]] = {name: [] for name in _ORDER}
    for number in numbers:
        for name, rows in demo_rows(_jury_id(number), _ASSIGNMENT[number], now, seed=number).items():
            tables[name].extend(rows)
    for row in tables["food"]:
        row["ingredients"] = json.dumps(row["ingredients"], ensure_ascii=False)
    for name in _ORDER:
        if tables[name]:
            op.bulk_insert(_table(name, *tables[name][0]), tables[name])


def downgrade() -> None:
    ids = ", ".join(f"'{_jury_id(number)}'" for number in range(1, _JURY_COUNT + 1))
    # Events, states, food, notes and notifications go with the pets (ON DELETE CASCADE).
    op.execute(f"DELETE FROM pets WHERE user_id IN ({ids})")
