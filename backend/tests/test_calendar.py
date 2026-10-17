import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from app.application.events.dto import EventCalendarItem
from app.domain.events.enums import EventPeriod, EventType
from app.presentation.http.calendar import render_calendar

_HEADER = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//PetCare//Pet care events//RU",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:PetCare",
]


def _item(**overrides) -> EventCalendarItem:
    values = {
        "id": uuid4(),
        "petId": uuid4(),
        "petName": "Барсик",
        "name": "Прививка от бешенства",
        "type": EventType.VACCINATION,
        "schedule": 1793527200.75,
        "period": EventPeriod.YEARLY,
        "description": None,
    }
    values.update(overrides)
    return EventCalendarItem(**values)


def _unfold(text: str) -> str:
    return text.replace("\r\n ", "")


def _logical_lines(text: str) -> list[str]:
    unfolded = _unfold(text)
    assert unfolded.endswith("\r\n")
    return unfolded.split("\r\n")[:-1]


def test_lines_use_crlf_including_the_trailing_break():
    text = render_calendar([_item()], alarm_minutes=0, now=1700000000.2)
    assert text.endswith("\r\n")
    assert "\n" not in text.replace("\r\n", "")
    assert text.startswith("BEGIN:VCALENDAR\r\n")
    assert text.endswith("END:VCALENDAR\r\n")


def test_empty_calendar_is_a_valid_vcalendar():
    text = render_calendar([], alarm_minutes=1440, now=1700000000)
    assert _logical_lines(text) == [*_HEADER, "END:VCALENDAR"]
    assert "VEVENT" not in text
    assert "VALARM" not in text


def test_header_footer_and_timestamps_drop_fractional_seconds():
    schedule = 1793527200.75
    now = 1700000000.2
    item = _item(schedule=schedule, period=EventPeriod.NONE, description="Нобивак")
    text = render_calendar([item], alarm_minutes=0, now=now)
    lines = _logical_lines(text)
    assert lines[: len(_HEADER)] == _HEADER
    assert lines[-1] == "END:VCALENDAR"
    start = datetime.fromtimestamp(int(schedule), UTC)
    stamp = datetime.fromtimestamp(int(now), UTC)
    assert f"UID:{item.id}@petcare" in lines
    assert f"DTSTAMP:{stamp.strftime('%Y%m%dT%H%M%SZ')}" in lines
    assert f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}" in lines
    assert f"DTEND:{(start + timedelta(hours=1)).strftime('%Y%m%dT%H%M%SZ')}" in lines
    for prefix in ("DTSTAMP:", "DTSTART:", "DTEND:"):
        value = next(line for line in lines if line.startswith(prefix)).split(":", 1)[1]
        assert re.fullmatch(r"\d{8}T\d{6}Z", value)


def test_text_escaping():
    item = _item(
        petName="a\\b",
        name="c;d,e",
        type=EventType.OTHER,
        period=EventPeriod.NONE,
        description="f\ng\r\nh\ri",
    )
    lines = _logical_lines(render_calendar([item], alarm_minutes=0, now=1700000000))
    assert "SUMMARY:a\\\\b: c\\;d\\,e" in lines
    assert "DESCRIPTION:Другое\\n\\nf\\ng\\nh\\ni" in lines
    assert "CATEGORIES:Другое" in lines


@pytest.mark.parametrize(
    ("type_", "label"),
    [
        (EventType.VACCINATION, "Прививка"),
        (EventType.PARASITE_TREATMENT, "Обработка от паразитов"),
        (EventType.VET_VISIT, "Визит к ветеринару"),
        (EventType.MEDICATION, "Лекарство"),
        (EventType.GROOMING, "Груминг"),
        (EventType.OTHER, "Другое"),
    ],
)
def test_type_labels(type_, label):
    item = _item(type=type_, period=EventPeriod.NONE, description="заметка")
    lines = _logical_lines(render_calendar([item], alarm_minutes=0, now=1700000000))
    assert "SUMMARY:Барсик: Прививка от бешенства" in lines
    assert f"DESCRIPTION:{label}\\n\\nзаметка" in lines
    assert f"CATEGORIES:{label}" in lines


def test_description_is_only_the_label_when_absent():
    lines = _logical_lines(render_calendar([_item(description=None)], alarm_minutes=0, now=1700000000))
    assert "DESCRIPTION:Прививка" in lines


@pytest.mark.parametrize(
    ("period", "rule"),
    [
        (EventPeriod.DAILY, "FREQ=DAILY"),
        (EventPeriod.WEEKLY, "FREQ=WEEKLY"),
        (EventPeriod.MONTHLY, "FREQ=MONTHLY"),
        (EventPeriod.QUARTERLY, "FREQ=MONTHLY;INTERVAL=3"),
        (EventPeriod.HALF_YEAR, "FREQ=MONTHLY;INTERVAL=6"),
        (EventPeriod.YEARLY, "FREQ=YEARLY"),
        (EventPeriod.NONE, None),
    ],
)
def test_rrule_for_every_period(period, rule):
    lines = _logical_lines(render_calendar([_item(period=period)], alarm_minutes=0, now=1700000000))
    if rule is None:
        assert all(not line.startswith("RRULE:") for line in lines)
    else:
        assert f"RRULE:{rule}" in lines


def test_alarm_present_by_default_and_absent_for_zero():
    item = _item()
    with_alarm = _logical_lines(render_calendar([item], alarm_minutes=1440, now=1700000000))
    assert "BEGIN:VALARM" in with_alarm
    assert "ACTION:DISPLAY" in with_alarm
    assert "TRIGGER:-PT1440M" in with_alarm
    assert "END:VALARM" in with_alarm
    summary = next(line for line in with_alarm if line.startswith("SUMMARY:"))
    assert summary.removeprefix("SUMMARY:") == next(
        line.removeprefix("DESCRIPTION:") for line in with_alarm if line.startswith("DESCRIPTION:Барсик")
    )
    alarm_at = with_alarm.index("BEGIN:VALARM")
    assert with_alarm.index("END:VALARM") < with_alarm.index("END:VEVENT")
    assert alarm_at > with_alarm.index("BEGIN:VEVENT")
    without = render_calendar([item], alarm_minutes=0, now=1700000000)
    assert "VALARM" not in without
    assert "TRIGGER" not in without


def test_folding_keeps_octets_and_cyrillic_characters_intact():
    pet_name = "Я" * 80
    description = "ё" * 90
    item = _item(petName=pet_name, name="Таблетка", description=description, period=EventPeriod.NONE)
    text = render_calendar([item], alarm_minutes=0, now=1700000000)
    raw = text.encode("utf-8")
    assert raw.endswith(b"\r\n")
    assert b"\r\n " in raw
    physical = raw.split(b"\r\n")
    assert physical[-1] == b""
    for line in physical[:-1]:
        assert len(line) <= 75
        line.decode("utf-8")
    unfolded = raw.replace(b"\r\n ", b"").decode("utf-8")
    assert f"SUMMARY:{pet_name}: Таблетка" in unfolded
    assert f"DESCRIPTION:Прививка\\n\\n{description}" in unfolded
    assert unfolded == _unfold(text)
