"""PDF export of a pet's history, checked on the same demo history the jury accounts get from migration 0009."""

import importlib.util
import io
import re
import uuid
from pathlib import Path
from time import time

import pytest
from alembic import command
from alembic.config import Config
from conftest import register_user
from sqlalchemy import insert

from app.application.reports.builder import build_report
from app.domain.breeds.entity import Breed
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryKind, CategoryType, CategoryUnit
from app.domain.events.entity import Event
from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.foods.entity import Food
from app.domain.pets.entity import Pet
from app.domain.states.entity import State
from app.infra.database import mappings
from app.infra.reports.pdf import render_pdf
from test_pets_endpoints import PNG_BYTES

pytestmark = pytest.mark.req("P.REPORT")

DAY = 86400.0
_MIGRATION = Path(__file__).parents[1] / "alembic" / "versions" / "0009_jury_demo_data.py"


def _seed_module():
    spec = importlib.util.spec_from_file_location("jury_demo_data", _MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


seed = _seed_module()
# SQLite gives UUID columns numeric affinity, so the all-digit catalog ids of the migration collapse there;
# tests load the same history with hex letters in those ids.
seed._breed_id = lambda number: uuid.UUID(f"00000000-0000-4000-8000-{number:011d}e")
seed._category_id = lambda number: uuid.UUID(f"00000000-0000-4000-9000-{number:011d}c")


async def _load_demo(db_session_factory, owner_id: str, templates: tuple[int, ...]) -> None:
    """Catalog rows the migrations seed in Postgres, then one owner's demo history."""
    rows = seed.demo_rows(uuid.UUID(owner_id), templates, time(), seed=1)
    async with db_session_factory() as session:
        animals = {
            uuid.UUID(f"00000000-0000-4000-a000-{n:012d}"): name
            for n, name in ((1, "Кошки"), (2, "Собаки"), (3, "Рыбки"))
        }
        await session.execute(insert(mappings.animals), [{"id": key, "name": name} for key, name in animals.items()])
        animal_of = {1: 1, 2: 1, 7: 1, 15: 1, 16: 1, 201: 3, 203: 3}
        breeds = [
            {
                "id": seed._breed_id(number),
                "animal_id": uuid.UUID(f"00000000-0000-4000-a000-{animal_of.get(number, 2):012d}"),
                "name": f"Порода {number}",
            }
            for number in seed._BREEDS.values()
        ]
        await session.execute(insert(mappings.breeds), breeds)
        kinds = {"weight": ("Вес", "last", "number", "g"), "water": ("Вода", "sum", "number", "ml"),
                 "walk": ("Прогулка", "sum", "number", "min"), "activity": ("Активность", "avg", "scale", "points"),
                 "appetite": ("Аппетит", "avg", "scale", "points"), "gi": ("Проблемы с ЖКТ", "count", "check", "none"),
                 "allergy": ("Аллергическая реакция", "count", "check", "none")}  # fmt: skip
        await session.execute(
            insert(mappings.categories),
            [
                {"id": seed._category_id(number), "name": kinds[key][0], "kind": CategoryKind(kinds[key][1]),
                 "type": CategoryType(kinds[key][2]), "unit": CategoryUnit(kinds[key][3])}
                for key, number in seed._CATEGORIES.items()
            ],
        )  # fmt: skip
        for table in ("pets", "events", "notifications", "states", "food", "notes"):
            if rows[table]:
                await session.execute(insert(getattr(mappings, table)), rows[table])
        await session.commit()


@pytest.fixture
async def demo_owner(client, db_session_factory):
    user_id, headers = register_user(client, login="demo")
    await _load_demo(db_session_factory, user_id, (0, 1))  # Барсик the cat and Рекс the shepherd
    return headers


def _pet_id(client, headers, name: str) -> str:
    pets = client.get("/api/v1/pets", headers=headers).json()["items"]
    return next(pet["id"] for pet in pets if pet["name"] == name)


@pytest.mark.req("5.1.4", "5.4.6", "P.CHECK")
def test_demo_history_reads_like_real_use(client, demo_owner):
    pets = client.get("/api/v1/pets", headers=demo_owner).json()
    assert sorted(pet["name"] for pet in pets["items"]) == ["Барсик", "Рекс"]
    upcoming = client.get("/api/v1/events/upcoming", params={"days": 30}, headers=demo_owner).json()["items"]
    assert any(item["isOverdue"] for item in upcoming)
    assert any(not item["isOverdue"] for item in upcoming)
    barsik = _pet_id(client, demo_owner, "Барсик")
    vaccinations = client.get(
        "/api/v1/events", params={"petId": barsik, "type": "vaccination", "status": "done"}, headers=demo_owner
    )
    assert vaccinations.json()["total"] >= 4
    salmon = next(
        food
        for food in client.get("/api/v1/foods", params={"petId": barsik, "size": 100}, headers=demo_owner).json()[
            "items"
        ]
        if food["isTolerability"] is False
    )
    suspects = client.get(f"/api/v1/foods/{salmon['id']}/suspects", headers=demo_owner).json()["suspects"]
    assert suspects == ["Лосось", "Горох"]


@pytest.mark.req("P.REPORT", "5.2.1", "5.2.5", "5.3.5")
def test_report_is_a_downloadable_pdf(client, demo_owner):
    response = client.get(f"/api/v1/pets/{_pet_id(client, demo_owner, 'Рекс')}/report", headers=demo_owner)
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/pdf"
    disposition = response.headers["content-disposition"]
    assert disposition.startswith(
        "attachment; filename=\"petcare-report.pdf\"; filename*=UTF-8''petcare-%D0%A0%D0%B5%D0%BA%D1%81-"
    )
    body = response.content
    assert body.startswith(b"%PDF-")
    assert len(re.findall(rb"/Type /Page\b", body)) >= 2


def test_report_includes_the_pet_photo(client, auth, pet_id):
    client.put(f"/api/v1/pets/{pet_id}/photo", files={"file": ("p.png", PNG_BYTES, "image/png")}, headers=auth)
    response = client.get(f"/api/v1/pets/{pet_id}/report", headers=auth)
    assert response.status_code == 200
    assert b"/Subtype /Image" in response.content


@pytest.mark.req("P.ACCESS")
def test_report_of_someone_elses_pet_is_not_found(client, pet_id):
    _, stranger = register_user(client, login="stranger")
    assert client.get(f"/api/v1/pets/{pet_id}/report", headers=stranger).status_code == 404
    assert client.get(f"/api/v1/pets/{pet_id}/report").status_code == 401


def _pet() -> Pet:
    return Pet(user_id=uuid.uuid4(), name="Барсик", birth_date=0.0, breed=Breed(animal_id=uuid.uuid4(), name="Сфинкс"))


def _event(name, type_, status, days, period=EventPeriod.NONE, description=None, now=1_800_000_000.0):
    return Event(
        pet_id=uuid.uuid4(), name=name, type=type_, status=status, schedule=now + days * DAY, period=period,
        description=description, done_at=now + days * DAY if status == EventStatus.DONE else None,
    )  # fmt: skip


@pytest.mark.req("P.REPORT", "5.4.1", "5.4.6")
def test_history_folds_into_procedures_and_monthly_activity():
    now = 1_800_000_000.0
    yearly = EventPeriod.YEARLY
    events = [
        _event("Бешенство", EventType.VACCINATION, EventStatus.DONE, -365, yearly, now=now),
        _event("Бешенство", EventType.VACCINATION, EventStatus.PLANNED, -3, yearly, now=now),
        _event("Капли", EventType.PARASITE_TREATMENT, EventStatus.DONE, -80, EventPeriod.QUARTERLY, now=now),
        _event("Капли", EventType.PARASITE_TREATMENT, EventStatus.PLANNED, 10, EventPeriod.QUARTERLY, now=now),
        _event("Осмотр", EventType.VET_VISIT, EventStatus.DONE, -20, description="Здоров", now=now),
    ]
    report = build_report(
        _pet(), events=events, states=[], categories={}, food_records=[], notes=[], photo=None, now=now
    )
    assert [(item.name, item.times_done, item.is_overdue) for item in report.procedures] == [
        ("Бешенство", 1, True),
        ("Капли", 1, False),
    ]
    assert report.overdue == 1
    assert [event.name for event in report.upcoming] == ["Бешенство", "Капли"]
    assert len(report.activity) == 12
    assert sum(month.done.get(EventType.VET_VISIT, 0) for month in report.activity) == 1
    assert sum(sum(month.done.values()) for month in report.activity) == 2  # the vaccine a year ago is outside
    assert [(note.title, note.text) for note in report.notes] == [("Осмотр", "Здоров")]


@pytest.mark.req("P.REPORT", "5.2.5", "5.3.2", "5.3.3", "5.3.4")
def test_measurements_and_food_become_series_and_verdicts():
    now = 1_800_000_000.0
    weight = Category(name="Вес", kind=CategoryKind.LAST, type=CategoryType.NUMBER, unit=CategoryUnit.G)
    appetite = Category(name="Аппетит", kind=CategoryKind.AVG, type=CategoryType.SCALE, unit=CategoryUnit.POINTS)
    gi = Category(name="Проблемы с ЖКТ", kind=CategoryKind.COUNT, type=CategoryType.CHECK, unit=CategoryUnit.NONE)
    pet_id = uuid.uuid4()
    states = [
        State(pet_id=pet_id, category_id=weight.id, value=grams, time=now - days * DAY)
        for grams, days in ((4800, 60), (4600, 30), (4500, 1))
    ]
    states += [State(pet_id=pet_id, category_id=appetite.id, value=v, time=now - DAY) for v in (3, 5)]
    states += [State(pet_id=pet_id, category_id=gi.id, value=1, time=now - 5 * DAY)]
    food = [
        Food(pet_id=pet_id, name="Курица", ingredients=["Курица", "Рис"], is_approach=True, is_tolerability=True, created_at=1),
        Food(pet_id=pet_id, name="Лосось", ingredients=["Лосось", "рис"], is_approach=False, is_tolerability=False,
             consequences="Зуд", created_at=2),
        Food(pet_id=pet_id, name="Курица", ingredients=["Курица"], created_at=3),
    ]  # fmt: skip
    categories = {category.id: category for category in (weight, appetite, gi)}
    report = build_report(
        _pet(), events=[], states=states, categories=categories, food_records=food, notes=[], photo=None, now=now
    )
    assert [(s.name, [v for _, v in s.points]) for s in report.series] == [("Вес", [4800, 4600, 4500])]
    assert [(s.name, s.average, s.count) for s in report.scales] == [("Аппетит", 4.0, 2)]
    assert [(c.name, c.count) for c in report.checks] == [("Проблемы с ЖКТ", 1)]
    assert [(f.name, f.times, f.suited, f.unsuited, f.reactions) for f in report.foods] == [
        ("Лосось", 1, 0, 1, ["Зуд"]),
        ("Курица", 2, 1, 0, []),
    ]
    assert report.tolerance == {"suited": 1, "unsuited": 1, "unknown": 1}
    assert report.suspects == ["Лосось"]
    assert render_pdf(report).startswith(b"%PDF-")


def test_empty_history_still_renders():
    report = build_report(
        _pet(), events=[], states=[], categories={}, food_records=[], notes=[], photo=b"not an image", now=time()
    )
    assert render_pdf(report).startswith(b"%PDF-")


@pytest.mark.req("P.ARCH", "P.CHECK")
def test_demo_data_migration_seeds_every_jury_account_in_place():
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "0008_states_category_id:0009_jury_demo_data", sql=True)
    sql = output.getvalue()
    assert sql.count("INSERT INTO pets") == sum(len(templates) for templates in seed._ASSIGNMENT.values())
    assert "INSERT INTO food" in sql and '["Курица", "Рис", "Кукуруза"]' in sql
    for number in range(1, 11):
        assert f"00000000-0000-4000-b000-{number:012d}" in sql
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=output)
    command.downgrade(config, "0009_jury_demo_data:0008_states_category_id", sql=True)
    assert "DELETE FROM pets WHERE user_id IN" in output.getvalue()


@pytest.mark.req("P.CHECK")
def test_each_jury_account_gets_its_own_pets():
    now = time()
    pets = {number: [p["name"] for p in seed.demo_rows(uuid.uuid4(), seed._ASSIGNMENT[number], now, number)["pets"]]
            for number in range(1, 11)}  # fmt: skip
    assert len({tuple(names) for names in pets.values()}) == 10
    assert {name for names in pets.values() for name in names} == {template.name for template in seed._TEMPLATES}
