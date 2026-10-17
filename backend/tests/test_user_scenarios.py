"""End-to-end user stories from "Задание PetCare", section 4: each test walks one scenario through the HTTP API
the way the frontend does, from registration to the final screen state."""

from datetime import UTC, datetime, timedelta

import pytest
from conftest import CAT_BREED_ID, CAT_ID
from test_pets_endpoints import PNG_BYTES

pytestmark = pytest.mark.integration

DAY = 86400.0


def _days_from_now(days: float) -> float:
    return (datetime.now(UTC) + timedelta(days=days)).timestamp()


@pytest.fixture
def owner(client):
    """A new owner who has just registered."""
    response = client.post(
        "/api/v1/auth/register", json={"login": "anna", "password": "barsik2024", "fullName": "Анна Петрова"}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


@pytest.fixture
def barsik(client, owner):
    response = client.post("/api/v1/pets", json={"name": "Барсик", "breedId": CAT_BREED_ID}, headers=owner)
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.req("S1", "5.1.1", "5.1.2", "5.1.3", "5.1.4", "P.AUTH")
def test_scenario_1_owner_adds_a_pet_with_photo(client, owner, tmp_path, monkeypatch):
    monkeypatch.setattr("app.infra.photos.di.get_media_dir", lambda: tmp_path)

    # The form offers species, then the breeds of the chosen species.
    animals = client.get("/api/v1/animals", headers=owner).json()["items"]
    assert CAT_ID in [animal["id"] for animal in animals]
    breeds = client.get("/api/v1/breeds", params={"animalId": CAT_ID}, headers=owner).json()["items"]
    assert [breed["id"] for breed in breeds] == [CAT_BREED_ID]

    birth_date = datetime(2024, 3, 15, tzinfo=UTC).timestamp()
    created = client.post(
        "/api/v1/pets", json={"name": "Барсик", "breedId": CAT_BREED_ID, "birthDate": birth_date}, headers=owner
    )
    assert created.status_code == 201, created.text
    pet = created.json()

    photo = client.put(
        f"/api/v1/pets/{pet['id']}/photo", files={"file": ("barsik.png", PNG_BYTES, "image/png")}, headers=owner
    )
    assert photo.status_code == 200, photo.text

    # "Мои питомцы" shows the card with everything entered.
    page = client.get("/api/v1/pets", headers=owner).json()
    assert page["total"] == 1
    card = page["items"][0]
    assert card["name"] == "Барсик"
    assert card["animal"]["id"] == CAT_ID
    assert card["breed"]["id"] == CAT_BREED_ID
    assert card["birthDate"] == birth_date
    assert card["ageMonths"] > 0
    assert card["photoUrl"] == photo.json()["photoUrl"]


@pytest.mark.req("S1", "5.1.1", "7.1")
def test_scenario_1_quick_form_highlights_the_missing_name(client, owner):
    response = client.post("/api/v1/pets", json={"name": "  ", "breedId": CAT_BREED_ID}, headers=owner)
    assert response.status_code == 422
    assert [error["field"] for error in response.json()["fieldErrors"]] == ["name"]
    assert client.get("/api/v1/pets", headers=owner).json()["total"] == 0


@pytest.mark.req("S2", "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5")
def test_scenario_2_owner_keeps_the_health_history(client, owner, barsik, system_categories):
    vaccinated_at = _days_from_now(-30)
    history = [
        {"name": "Комплексная вакцина", "type": "vaccination", "schedule": vaccinated_at, "status": "done"},
        {"name": "Капли от блох", "type": "parasite_treatment", "schedule": _days_from_now(-20), "status": "done"},
        {
            "name": "Осмотр у терапевта",
            "type": "vet_visit",
            "schedule": _days_from_now(-10),
            "status": "done",
            "description": "Здоров. Рекомендован контроль веса через месяц.",
        },
    ]
    for event in history:
        response = client.post("/api/v1/events", json={"petId": barsik, **event}, headers=owner)
        assert response.status_code == 201, response.text
    conclusion = client.post(
        "/api/v1/notes",
        json={"petId": barsik, "content": "Заключение: лёгкий избыток веса, диета 2 недели"},
        headers=owner,
    )
    assert conclusion.status_code == 201, conclusion.text

    for days_ago, grams in ((14, 4800), (1, 4650)):
        response = client.post(
            "/api/v1/states",
            json={
                "petId": barsik,
                "categoryId": system_categories["weight"],
                "value": grams,
                "time": _days_from_now(-days_ago),
            },
            headers=owner,
        )
        assert response.status_code == 201, response.text

    # "Карта здоровья": each tab is a filter over the same history.
    def history_of(event_type):
        params = {"petId": barsik, "type": event_type}
        return client.get("/api/v1/events", params=params, headers=owner).json()["items"]

    vaccinations = history_of("vaccination")
    assert [(item["name"], item["schedule"], item["status"]) for item in vaccinations] == [
        ("Комплексная вакцина", vaccinated_at, "done")
    ]
    assert len(history_of("parasite_treatment")) == 1
    assert history_of("vet_visit")[0]["description"].startswith("Здоров")
    notes = client.get("/api/v1/notes", params={"petId": barsik}, headers=owner).json()["items"]
    assert notes[0]["content"].startswith("Заключение")

    weight = client.get(
        "/api/v1/states/summary", params={"petId": barsik, "categoryId": system_categories["weight"]}, headers=owner
    ).json()
    assert weight["value"] == 4650
    assert weight["count"] == 2


@pytest.mark.req("S3", "5.3.1", "5.3.2", "5.3.3", "5.3.4", "5.3.5")
def test_scenario_3_owner_learns_which_food_suits_the_pet(client, owner, barsik):
    def feed(**food):
        response = client.post("/api/v1/foods", json={"petId": barsik, **food}, headers=owner)
        assert response.status_code == 201, response.text
        return response.json()

    feed(name="Курица с рисом", ingredients=["Курица", "Рис"], isApproach=True, isTolerability=True)
    feed(name="Индейка", ingredients=["Индейка", "Рис"], isApproach=True, isTolerability=True)
    salmon = feed(
        name="Лосось с горохом",
        ingredients=["Лосось", "Горох", "рис"],
        isApproach=False,
        isTolerability=False,
        consequences="Зуд и покраснение кожи через 2 часа: аллергическая реакция",
    )

    # The personal base: what suited, what did not, and which ingredients to suspect.
    def foods(**filters):
        page = client.get("/api/v1/foods", params={"petId": barsik, **filters}, headers=owner).json()
        return sorted(item["name"] for item in page["items"])

    assert foods(isTolerability="true") == ["Индейка", "Курица с рисом"]
    assert foods(isTolerability="false") == ["Лосось с горохом"]
    assert foods(isApproach="false") == ["Лосось с горохом"]
    assert client.get("/api/v1/foods", params={"petId": barsik}, headers=owner).json()["total"] == 3

    suspects = client.get(f"/api/v1/foods/{salmon['id']}/suspects", headers=owner).json()
    assert suspects["suspects"] == ["Лосось", "Горох"]
    reaction = client.get(f"/api/v1/foods/{salmon['id']}", headers=owner).json()
    assert "аллергическая" in reaction["consequences"]


@pytest.mark.req("S4", "5.4.1", "5.4.2", "5.4.5", "5.4.6")
def test_scenario_4_owner_follows_upcoming_procedures(client, owner, barsik):
    def plan(**event):
        response = client.post("/api/v1/events", json={"petId": barsik, **event}, headers=owner)
        assert response.status_code == 201, response.text
        return response.json()

    overdue_vaccine = plan(name="Бешенство", type="vaccination", schedule=_days_from_now(-3), period="yearly")
    deworming = plan(name="Дегельминтизация", type="parasite_treatment", schedule=_days_from_now(5), period="quarterly")
    plan(name="Груминг", type="grooming", schedule=_days_from_now(90))
    assert deworming["nextSchedule"] is not None
    assert deworming["nextSchedule"] - deworming["schedule"] >= 89 * DAY

    reminder = client.post(
        "/api/v1/notifications", json={"eventId": deworming["id"], "time": _days_from_now(-0.01)}, headers=owner
    )
    assert reminder.status_code == 201, reminder.text

    # "Напоминания": what is due in the next month, overdue first.
    upcoming = client.get("/api/v1/events/upcoming", params={"days": 30}, headers=owner).json()["items"]
    assert [(item["name"], item["isOverdue"]) for item in upcoming] == [
        ("Бешенство", True),
        ("Дегельминтизация", False),
    ]
    due = client.get("/api/v1/notifications", params={"due": "true"}, headers=owner).json()["items"]
    assert [item["eventName"] for item in due] == ["Дегельминтизация"]

    # The vaccine is done three days late: the next one is due a year after the actual date.
    done_at = _days_from_now(0)
    completed = client.post(
        f"/api/v1/events/{overdue_vaccine['id']}/complete", json={"doneAt": done_at}, headers=owner
    ).json()
    next_vaccine = completed["nextEvent"]
    assert next_vaccine["status"] == "planned"
    assert 365 * DAY <= next_vaccine["schedule"] - done_at <= 366 * DAY

    upcoming = client.get("/api/v1/events/upcoming", params={"days": 30}, headers=owner).json()["items"]
    assert [item["name"] for item in upcoming] == ["Дегельминтизация"]
    read = client.patch(f"/api/v1/notifications/{due[0]['id']}", json={"status": "read"}, headers=owner)
    assert read.json()["status"] == "read"
    assert client.get("/api/v1/notifications", params={"due": "true"}, headers=owner).json()["total"] == 0


@pytest.mark.req("P.ACCESS")
def test_another_owner_sees_nothing_of_barsik(client, barsik):
    response = client.post(
        "/api/v1/auth/register", json={"login": "boris", "password": "rex2024ok", "fullName": "Борис"}
    )
    stranger = {"Authorization": f"Bearer {response.json()['accessToken']}"}
    assert client.get("/api/v1/pets", headers=stranger).json()["total"] == 0
    assert client.get(f"/api/v1/pets/{barsik}", headers=stranger).status_code == 404
    assert client.get("/api/v1/events/upcoming", headers=stranger).json()["total"] == 0
