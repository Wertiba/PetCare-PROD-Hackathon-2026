"""Requirement coverage: which items of the PetCare brief the test suite checks.

Tests declare what they verify with ``@pytest.mark.req("5.1.1", ...)`` (or a module-level ``pytestmark``).
At the end of the run the terminal shows a per-requirement summary, and ``--req-report=PATH`` writes it as
Markdown. Ids absent from ``REQUIREMENTS`` fail collection, so the catalog and the tests cannot drift apart.
"""

from collections import defaultdict
from pathlib import Path

import pytest

# id -> (group, title). Ids 5.x follow the numbering of "Задание PetCare", section 5.
REQUIREMENTS: dict[str, tuple[str, str]] = {
    "S1": ("Сценарии", "Сценарий 1. Добавление питомца"),
    "S2": ("Сценарии", "Сценарий 2. Ведение истории здоровья"),
    "S3": ("Сценарии", "Сценарий 3. Учёт питания"),
    "S4": ("Сценарии", "Сценарий 4. Контроль предстоящих процедур"),
    "5.1.1": ("5.1 Карточки питомцев", "Создание карточки питомца"),
    "5.1.2": ("5.1 Карточки питомцев", "Имя, вид, порода и дата рождения"),
    "5.1.3": ("5.1 Карточки питомцев", "Добавление фотографии"),
    "5.1.4": ("5.1 Карточки питомцев", "Список питомцев пользователя"),
    "5.2.1": ("5.2 Карта здоровья", "История вакцинаций с датами"),
    "5.2.2": ("5.2 Карта здоровья", "История обработок от паразитов"),
    "5.2.3": ("5.2 Карта здоровья", "Записи о посещениях ветеринара"),
    "5.2.4": ("5.2 Карта здоровья", "Хранение заключений ветеринаров"),
    "5.2.5": ("5.2 Карта здоровья", "Учёт веса и других параметров"),
    "5.3.1": ("5.3 Учёт питания", "Записи о кормах"),
    "5.3.2": ("5.3 Учёт питания", "Оценка «понравилось / не понравилось»"),
    "5.3.3": ("5.3 Учёт питания", "Оценка «подошло / не подошло»"),
    "5.3.4": ("5.3 Учёт питания", "Нежелательные реакции: ЖКТ, аллергия"),
    "5.3.5": ("5.3 Учёт питания", "История питания и личная база предпочтений"),
    "5.4.1": ("5.4 Напоминания и назначения", "Расчёт даты следующей вакцинации"),
    "5.4.2": ("5.4 Напоминания и назначения", "Расчёт даты следующей обработки от паразитов"),
    "5.4.3": ("5.4 Напоминания и назначения", "Назначения препаратов из ветеринарных заключений"),
    "5.4.4": ("5.4 Напоминания и назначения", "Длительность и регулярность приёма препаратов"),
    "5.4.5": ("5.4 Напоминания и назначения", "Формирование напоминаний"),
    "5.4.6": ("5.4 Напоминания и назначения", "Список ближайших событий"),
    "5.4.7": ("5.4 Напоминания и назначения", "Уведомления через push или виджет"),
    "7.1": ("7–8 UX и ограничения", "Понятные ошибки форм с указанием проблемного поля"),
    "P.REPORT": ("Дополнительные функции", "Экспорт истории питомца в PDF с графиками"),
    "P.AUTH": ("Платформа", "Регистрация, вход, обновление токена, выход"),
    "P.ACCESS": ("Платформа", "Изоляция данных пользователей и права ролей"),
    "P.CATALOG": ("Платформа", "Справочник видов, пород и категорий"),
    "P.TX": ("Платформа", "Транзакции: Unit of Work и откаты"),
    "P.TIME": ("Платформа", "Единый формат времени (Unix seconds, UTC)"),
    "P.OBS": ("Платформа", "Наблюдаемость: trace id, логи, метрики, health"),
    "P.ARCH": ("Платформа", "Контракт API, схема БД, границы слоёв"),
    "P.CHECK": ("Платформа", "Демо-данные жюри: разные питомцы и история"),
}


def pytest_addoption(parser):
    parser.addoption("--req-report", metavar="PATH", help="write requirement coverage as Markdown to PATH")


def pytest_configure(config):
    config.addinivalue_line("markers", "req(*ids): requirements from req_coverage.REQUIREMENTS the test verifies")
    config.pluginmanager.register(_RequirementCoverage(config), "req-coverage")


class _RequirementCoverage:
    def __init__(self, config) -> None:
        self.config = config
        self.results: dict[str, list[tuple[str, str]]] = defaultdict(list)

    def pytest_collection_modifyitems(self, items):
        unknown = sorted(
            {
                f"{item.nodeid}: {req_id}"
                for item in items
                for marker in item.iter_markers("req")
                for req_id in marker.args
                if req_id not in REQUIREMENTS
            }
        )
        if unknown:
            raise pytest.UsageError("Unknown requirement ids:\n" + "\n".join(unknown))

    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_makereport(self, item, call):
        report = yield
        report.req_ids = sorted({req_id for marker in item.iter_markers("req") for req_id in marker.args})
        return report

    def pytest_runtest_logreport(self, report):
        # Record each test once: its call phase, or the phase that stopped it before the call.
        if report.when == "call" or (report.when == "setup" and not report.passed):
            outcome = "passed" if report.passed else "skipped" if report.skipped else "failed"
            for req_id in getattr(report, "req_ids", []):
                self.results[req_id].append((report.nodeid, outcome))

    def pytest_terminal_summary(self, terminalreporter):
        if not self.results:
            return
        terminalreporter.section("requirement coverage")
        for req_id, (_, title) in REQUIREMENTS.items():
            tests = self.results.get(req_id, [])
            terminalreporter.write_line(f"{req_id:<10} {len(tests):>3}  {_status(tests):<14} {title}")
        path = self.config.getoption("--req-report")
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(_markdown(self.results), encoding="utf-8")
            terminalreporter.write_line(f"requirement coverage written to {path}")


def _status(results: list[tuple[str, str]]) -> str:
    if not results:
        return "⚪ нет тестов"
    if any(outcome == "failed" for _, outcome in results):
        return "❌ падает"
    return "✅ покрыто"


def _markdown(results: dict[str, list[tuple[str, str]]]) -> str:
    covered = sum(1 for req_id in REQUIREMENTS if results.get(req_id) and _status(results[req_id]) == "✅ покрыто")
    lines = [
        "# Покрытие требований тестами",
        "",
        f"Покрыто требований: **{covered} из {len(REQUIREMENTS)}**. "
        "Отчёт генерирует `pytest --req-report=PATH` по маркерам `@pytest.mark.req`.",
        "",
    ]
    group = None
    for req_id, (req_group, title) in REQUIREMENTS.items():
        if req_group != group:
            group = req_group
            lines += ["", f"## {group}", "", "| Id | Требование | Тестов | Статус |", "|---|---|---|---|"]
        tests = results.get(req_id, [])
        lines.append(f"| {req_id} | {title} | {len(tests)} | {_status(tests)} |")
    lines += ["", "## Тесты по требованиям", ""]
    for req_id, (_, title) in REQUIREMENTS.items():
        tests = results.get(req_id, [])
        if tests:
            lines.append(f"<details><summary>{req_id} — {title} ({len(tests)})</summary>\n")
            lines += [f"- `{nodeid}` — {outcome}" for nodeid, outcome in sorted(tests)]
            lines.append("\n</details>\n")
    return "\n".join(lines) + "\n"
