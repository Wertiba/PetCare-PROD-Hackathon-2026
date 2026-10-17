import ast
import json
from pathlib import Path
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable
from app.infra.database.mappings import metadata
from app.main import app

FIXTURES = Path(__file__).parent / "fixtures"
SOURCE = Path(__file__).parents[1] / "src" / "app"


def test_openapi_matches_the_documented_api_contract():
    assert app.openapi() == json.loads((Path(__file__).parents[1] / "docs" / "openapi.json").read_text())


def test_postgres_schema_matches_documented_tables_and_indexes():
    actual = {
        table.name: {
            "table": str(CreateTable(table).compile(dialect=dialect())),
            "indexes": sorted((str(CreateIndex(index).compile(dialect=dialect())) for index in table.indexes)),
        }
        for table in metadata.sorted_tables
    }
    assert actual == json.loads((FIXTURES / "schema.json").read_text())


def test_inner_layers_do_not_import_frameworks_or_outer_layers():
    forbidden = {
        "sqlalchemy",
        "fastapi",
        "pydantic",
        "dynaconf",
        "prometheus_client",
        "jwt",
        "passlib",
        "loguru",
        "anyio",
    }
    for layer in ("domain", "application"):
        for path in (SOURCE / layer).rglob("*.py"):
            imports = []
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    imports.extend((alias.name for alias in node.names))
                elif isinstance(node, ast.ImportFrom):
                    assert node.level == 0, f"Use explicit layer imports in {path}"
                    imports.append(node.module or "")
            for module in imports:
                assert module.split(".")[0] not in forbidden, (path, module)
                assert not module.startswith(("app.infra", "app.presentation", "app.bootstrap", "app.main")), (
                    path,
                    module,
                )
                if layer == "domain":
                    assert not module.startswith("app.application"), (path, module)
                if module.startswith("dishka"):
                    assert layer == "application" and path.name == "di.py", (path, module)
