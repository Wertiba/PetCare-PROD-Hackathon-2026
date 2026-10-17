import uuid
from conftest import register_user


def _feed(client, headers, pet_id, **overrides):
    payload = {"petId": pet_id, "name": "Royal Canin", "weight": 50, "ingredients": ["Курица", "Рис"]}
    payload.update(overrides)
    response = client.post("/api/v1/foods", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_crud(client, auth, pet_id):
    food = _feed(client, auth, pet_id, ingredients=[" Курица ", "рис", "курица", "  "], isApproach=True)
    assert food["ingredients"] == ["Курица", "рис"]
    assert food["isApproach"] is True
    assert food["isTolerability"] is None
    assert food["consequences"] is None
    assert client.get(f"/api/v1/foods/{food['id']}", headers=auth).json() == food
    updated = client.patch(
        f"/api/v1/foods/{food['id']}",
        json={"isTolerability": False, "consequences": "Рвота", "ingredients": ["Утка"]},
        headers=auth,
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["isTolerability"] is False
    assert body["consequences"] == "Рвота"
    assert body["ingredients"] == ["Утка"]
    assert body["name"] == "Royal Canin"
    assert client.delete(f"/api/v1/foods/{food['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/foods/{food['id']}", headers=auth).status_code == 404


def test_list_filters(client, auth, pet_id):
    _feed(client, auth, pet_id, name="A", isApproach=True, isTolerability=True)
    _feed(client, auth, pet_id, name="B", isApproach=False, isTolerability=False)
    _feed(client, auth, pet_id, name="C")
    everything = client.get("/api/v1/foods", params={"petId": pet_id}, headers=auth).json()
    assert [item["name"] for item in everything["items"]] == ["C", "B", "A"]
    liked = client.get("/api/v1/foods", params={"isApproach": "true"}, headers=auth).json()
    assert [item["name"] for item in liked["items"]] == ["A"]
    bad = client.get("/api/v1/foods", params={"isTolerability": "false"}, headers=auth).json()
    assert [item["name"] for item in bad["items"]] == ["B"]


def test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food(client, auth, pet_id):
    _feed(client, auth, pet_id, ingredients=["Курица", "Рис"], isTolerability=True)
    _feed(client, auth, pet_id, ingredients=["Говядина"], isTolerability=False)
    _feed(client, auth, pet_id, ingredients=["Индейка"])
    _feed(client, auth, pet_id, ingredients=["Морковь"], isTolerability=True)
    poisoned = _feed(client, auth, pet_id, ingredients=["курица", "Говядина", "Индейка", "Морковь", "Горох"])
    later = _feed(client, auth, pet_id, ingredients=["Горох"], isTolerability=True)
    response = client.get(f"/api/v1/foods/{poisoned['id']}/suspects", headers=auth)
    assert response.status_code == 200
    assert response.json() == {
        "foodId": poisoned["id"],
        "petId": pet_id,
        "suspects": ["Говядина", "Индейка", "Горох"],
        "comparedFoods": 2,
    }
    assert client.get(f"/api/v1/foods/{later['id']}/suspects", headers=auth).json()["suspects"] == ["Горох"]


def test_everything_is_suspect_without_tolerated_history(client, auth, pet_id):
    first = _feed(client, auth, pet_id, ingredients=["Курица", "Рис"])
    response = client.get(f"/api/v1/foods/{first['id']}/suspects", headers=auth).json()
    assert response["suspects"] == ["Курица", "Рис"]
    assert response["comparedFoods"] == 0


def test_other_users_food_is_invisible(client, auth, pet_id):
    food_id = _feed(client, auth, pet_id)["id"]
    _, stranger = register_user(client, login="stranger")
    for method in ("get", "delete"):
        assert client.request(method, f"/api/v1/foods/{food_id}", headers=stranger).status_code == 404
    assert client.patch(f"/api/v1/foods/{food_id}", json={"name": "x"}, headers=stranger).status_code == 404
    assert client.get(f"/api/v1/foods/{food_id}/suspects", headers=stranger).status_code == 404
    assert client.get("/api/v1/foods", headers=stranger).json()["total"] == 0
    foreign = client.post("/api/v1/foods", json={"petId": pet_id, "name": "x"}, headers=stranger)
    assert foreign.status_code == 422
    assert foreign.json()["code"] == "PET_NOT_FOUND"


def test_validation(client, auth, pet_id):
    for payload in (
        {"petId": pet_id, "name": "  "},
        {"petId": pet_id, "name": "x", "weight": -1},
        {"petId": pet_id, "name": "x", "ingredients": None},
        {"petId": pet_id, "name": "x", "ingredients": ["x" * 101]},
    ):
        assert client.post("/api/v1/foods", json=payload, headers=auth).status_code == 422, payload
    food_id = _feed(client, auth, pet_id)["id"]
    assert client.patch(f"/api/v1/foods/{food_id}", json={"ingredients": None}, headers=auth).status_code == 422


def test_requires_auth(client):
    assert client.get("/api/v1/foods").status_code == 401
    assert client.get(f"/api/v1/foods/{uuid.uuid4()}/suspects").status_code == 401
