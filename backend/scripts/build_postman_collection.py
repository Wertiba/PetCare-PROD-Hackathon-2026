"""Build docs/petcare.postman_collection.json from the OpenAPI schema.

Run from backend/: `uv run python scripts/build_postman_collection.py`.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "tests")
import conftest  # noqa: E402,F401  (test env defaults)

from app.main import app  # noqa: E402

spec = app.openapi()
schemas = spec["components"]["schemas"]

# Path/body field -> collection variable holding the id of the last created object.
ID_VARS = {
    "pet_id": "petId",
    "petId": "petId",
    "animal_id": "animalId",
    "animalId": "animalId",
    "breed_id": "breedId",
    "breedId": "breedId",
    "category_id": "categoryId",
    "categoryId": "categoryId",
    "state_id": "stateId",
    "event_id": "eventId",
    "eventId": "eventId",
    "notification_id": "notificationId",
    "note_id": "noteId",
    "food_id": "foodId",
}
# Created object of a POST /<resource> -> variable to save its id into.
CREATED_VAR = {
    "/api/v1/pets": "petId",
    "/api/v1/animals": "animalId",
    "/api/v1/breeds": "breedId",
    "/api/v1/categories": "categoryId",
    "/api/v1/states": "stateId",
    "/api/v1/events": "eventId",
    "/api/v1/notifications": "notificationId",
    "/api/v1/notes": "noteId",
    "/api/v1/foods": "foodId",
}
EXAMPLES = {
    "login": "жюри1",
    "password": "qwerty12345",
    "fullName": "Жюри 1",
    "name": "Барсик",
    "content": "Боится пылесоса",
    "description": "Комплексная прививка",
    "ingredients": ["Курица", "Рис"],
    "weight": 50,
    "consequences": None,
    "isApproach": True,
    "isTolerability": True,
    "value": 4200,
    "note": "После еды",
}
BODIES = {  # whole-body overrides where field-by-field examples would not make sense
    ("/api/v1/animals", "post"): {"name": "Хомяк"},
    ("/api/v1/breeds", "post"): {"animalId": "{{animalId}}", "name": "Джунгарский"},
    ("/api/v1/categories", "post"): {"name": "Прогулки в парке", "kind": "count", "type": "check", "unit": "none"},
    ("/api/v1/events", "post"): {
        "petId": "{{petId}}",
        "name": "Прививка от бешенства",
        "type": "vaccination",
        "schedule": 1798761600,
        "period": "yearly",
    },
    ("/api/v1/states", "post"): {"petId": "{{petId}}", "categoryId": "{{categoryId}}", "value": 1},
    ("/api/v1/foods", "post"): {
        "petId": "{{petId}}",
        "name": "Royal Canin Sterilised",
        "weight": 50,
        "ingredients": ["Курица", "Рис"],
        "isApproach": True,
        "isTolerability": None,
        "consequences": None,
    },
    ("/api/v1/animals/{animal_id}", "patch"): {"name": "Грызун"},
    ("/api/v1/breeds/{breed_id}", "patch"): {"name": "Джунгарский хомячок"},
    ("/api/v1/pets/{pet_id}", "patch"): {"name": "Барсик Второй", "birthDate": 1579046400},
    ("/api/v1/pets/{pet_id}/photo/upload-url", "post"): {"contentType": "image/jpeg", "size": 1024},
    ("/api/v1/pets/{pet_id}/photo/confirm", "post"): {
        "key": "pets/{{petId}}/photo/00000000-0000-4000-8000-000000000001.jpg"
    },
    ("/api/v1/categories/{category_id}", "patch"): {"name": "Прогулки у реки"},
    ("/api/v1/events/{event_id}", "patch"): {"description": "Взять ветпаспорт"},
    ("/api/v1/notifications/{notification_id}", "patch"): {"status": "read"},
    ("/api/v1/notifications/settings", "patch"): {"webPushEnabled": False},
    ("/api/v1/notifications/web-push/subscriptions", "post"): {
        "endpoint": "https://push.example.com/subscription/1",
        "keys": {"p256dh": "p256dh-key", "auth": "auth-key"},
    },
    ("/api/v1/notifications/web-push/subscriptions", "delete"): {"endpoint": "https://push.example.com/subscription/1"},
    ("/api/v1/states/{state_id}", "patch"): {"value": 0, "note": "Передумали"},
    ("/api/v1/notes/{note_id}", "patch"): {"content": "Уже не боится пылесоса"},
    ("/api/v1/foods/{food_id}", "patch"): {"isTolerability": False, "consequences": "Рвота через час после еды"},
}
FOLDERS = [
    "Auth",
    "Users",
    "Animals",
    "Breeds",
    "Pets",
    "Categories",
    "States",
    "Events",
    "Notifications",
    "Notes",
    "Foods",
    "Health",
]


def resolve(schema: dict) -> dict:
    while "$ref" in schema:
        schema = schemas[schema["$ref"].rsplit("/", 1)[-1]]
    if "anyOf" in schema:
        options = [option for option in schema["anyOf"] if option.get("type") != "null"]
        return resolve(options[0]) if options else {"type": "null"}
    return schema


def example(name: str, schema: dict):
    if name in ID_VARS:
        return f"{{{{{ID_VARS[name]}}}}}"
    if name in EXAMPLES:
        return EXAMPLES[name]
    schema = resolve(schema)
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        return {key: example(key, value) for key, value in schema.get("properties", {}).items()}
    if kind == "array":
        return [example(name, schema.get("items", {}))]
    return {"string": "text", "integer": 1, "number": 1, "boolean": True}.get(kind)


def body_for(path: str, method: str, operation: dict):
    if (path, method) in BODIES:
        return BODIES[path, method]
    content = operation.get("requestBody", {}).get("content", {})
    if "application/json" not in content:
        return None
    schema = resolve(content["application/json"]["schema"])
    required = set(schema.get("required", []))
    fields = schema.get("properties", {})
    # PATCH bodies: send just one meaningful field instead of every optional one.
    if method == "patch":
        first = next(iter(fields))
        return {first: example(first, fields[first])}
    return {key: example(key, value) for key, value in fields.items() if key in required or key in EXAMPLES}


def script(lines: list[str]) -> list[dict]:
    return [{"listen": "test", "script": {"type": "text/javascript", "exec": lines}}]


folders: dict[str, list] = {name: [] for name in FOLDERS}
for path, methods in spec["paths"].items():
    for method, operation in methods.items():
        tag = (operation.get("tags") or ["Health"])[0]
        url_path = re.sub(r"\{(\w+)\}", lambda m: f"{{{{{ID_VARS.get(m.group(1), m.group(1))}}}}}", path)
        query = [
            {
                "key": p["name"],
                "value": f"{{{{{ID_VARS[p['name']]}}}}}" if p.get("required") and p["name"] in ID_VARS else "",
                "description": p.get("description", ""),
                "disabled": not p.get("required", False),
            }
            for p in operation.get("parameters", [])
            if p["in"] == "query"
        ]
        request = {
            "method": method.upper(),
            "header": [],
            "url": {
                "raw": "{{baseUrl}}" + url_path,
                "host": ["{{baseUrl}}"],
                "path": [part for part in url_path.split("/") if part],
                "query": query,
            },
            "description": operation.get("description") or operation.get("summary", ""),
        }
        if path.startswith("/health") or path == "/metrics" or path in ("/api/v1/auth/register", "/api/v1/auth/login"):
            request["auth"] = {"type": "noauth"}
        if "multipart/form-data" in operation.get("requestBody", {}).get("content", {}):
            request["body"] = {
                "mode": "formdata",
                "formdata": [{"key": "file", "type": "file", "src": "", "description": "jpeg, png or webp up to 5 MB"}],
            }
        elif (body := body_for(path, method, operation)) is not None:
            request["header"].append({"key": "Content-Type", "value": "application/json"})
            request["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2)}
        item = {"name": operation.get("summary", f"{method.upper()} {path}"), "request": request}
        if path in ("/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/refresh"):
            item["event"] = script(
                [
                    "if (pm.response.code < 300) {",
                    "  pm.collectionVariables.set('accessToken', pm.response.json().accessToken);",
                    "}",
                ]
            )
        elif method == "post" and path in CREATED_VAR:
            item["event"] = script(
                [
                    "if (pm.response.code === 201) {",
                    f"  pm.collectionVariables.set('{CREATED_VAR[path]}', pm.response.json().id);",
                    "}",
                ]
            )
        folders.setdefault(tag, []).append(item)

if "/api/v1/auth/register" in spec["paths"]:
    # Register a fresh user by default so it never clashes with the seeded жюри accounts.
    for item in folders["Auth"]:
        if item["request"]["url"]["raw"].endswith("/auth/register"):
            item["request"]["body"]["raw"] = json.dumps(
                {"login": "user{{$timestamp}}", "password": "qwerty12345", "fullName": "Тестовый пользователь"},
                ensure_ascii=False,
                indent=2,
            )

# Pets need a breed: fetch one before creating a pet if breedId is still empty.
for item in folders["Breeds"]:
    if item["request"]["method"] == "GET" and item["request"]["url"]["raw"].endswith("/breeds"):
        item["event"] = script(
            [
                "const items = pm.response.json().items || [];",
                "if (items.length && !pm.collectionVariables.get('breedId')) {",
                "  pm.collectionVariables.set('breedId', items[0].id);",
                "}",
            ]
        )
for item in folders["Animals"]:
    if item["request"]["method"] == "GET" and item["request"]["url"]["raw"].endswith("/animals"):
        item["event"] = script(
            [
                "const items = pm.response.json().items || [];",
                "if (items.length && !pm.collectionVariables.get('animalId')) {",
                "  pm.collectionVariables.set('animalId', items[0].id);",
                "}",
            ]
        )
for item in folders["Categories"]:
    if item["request"]["method"] == "GET" and item["request"]["url"]["raw"].endswith("/categories"):
        item["event"] = script(
            [
                "const items = pm.response.json().items || [];",
                "if (items.length && !pm.collectionVariables.get('categoryId')) {",
                "  pm.collectionVariables.set('categoryId', items[0].id);",
                "}",
            ]
        )

# Deletes and logout last, children before parents, so running the whole collection works top to bottom.
CLEANUP_ORDER = [
    "Foods",
    "Notes",
    "Notifications",
    "Events",
    "States",
    "Categories",
    "Pets",
    "Breeds",
    "Animals",
    "Auth",
]
cleanup = []
for name in CLEANUP_ORDER:
    keep = []
    for item in folders.get(name, []):
        is_logout = item["request"]["url"]["raw"].endswith("/auth/logout")
        (cleanup if item["request"]["method"] == "DELETE" or is_logout else keep).append(item)
    folders[name] = keep
folders["Cleanup"] = cleanup

variables = ["baseUrl", "accessToken", *dict.fromkeys(ID_VARS.values())]
collection = {
    "info": {
        "name": "PetCare API",
        "description": (
            "Generated from docs/openapi.json.\n\n"
            "1. Auth → Login (жюри1 / qwerty12345) or Register: saves accessToken.\n"
            "2. Animals → list, Breeds → list: save animalId and breedId.\n"
            "3. Pets → Create Pet saves petId; every POST saves the id of what it created.\n"
            "Admin-only requests (create/update/delete animals and breeds) need a user with role ADMIN."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{accessToken}}", "type": "string"}]},
    "variable": [{"key": name, "value": "http://localhost:8080" if name == "baseUrl" else ""} for name in variables],
    "item": [{"name": name, "item": items} for name, items in folders.items() if items],
}
out = Path("docs/petcare.postman_collection.json")
out.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n")
print(out, sum(len(f["item"]) for f in collection["item"]), "requests")  # noqa: T201
