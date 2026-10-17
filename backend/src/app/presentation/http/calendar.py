from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from app.application.events.dto import EventCalendarItem
from app.domain.events.enums import EventPeriod, EventType

_CRLF = "\r\n"
_MAX_OCTETS = 75
_EVENT_LENGTH = timedelta(hours=1)
_TYPE_LABELS = {
    EventType.VACCINATION: "Прививка",
    EventType.PARASITE_TREATMENT: "Обработка от паразитов",
    EventType.VET_VISIT: "Визит к ветеринару",
    EventType.MEDICATION: "Лекарство",
    EventType.GROOMING: "Груминг",
    EventType.OTHER: "Другое",
}
_RRULES = {
    EventPeriod.DAILY: "FREQ=DAILY",
    EventPeriod.WEEKLY: "FREQ=WEEKLY",
    EventPeriod.MONTHLY: "FREQ=MONTHLY",
    EventPeriod.QUARTERLY: "FREQ=MONTHLY;INTERVAL=3",
    EventPeriod.HALF_YEAR: "FREQ=MONTHLY;INTERVAL=6",
    EventPeriod.YEARLY: "FREQ=YEARLY",
}


def render_calendar(items: Sequence[EventCalendarItem], *, alarm_minutes: int, now: float) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PetCare//Pet care events//RU",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:PetCare",
    ]
    for item in items:
        lines.extend(_event_lines(item, alarm_minutes=alarm_minutes, now=now))
    lines.append("END:VCALENDAR")
    return _CRLF.join(_fold(line) for line in lines) + _CRLF


def _event_lines(item: EventCalendarItem, *, alarm_minutes: int, now: float) -> list[str]:
    label = _TYPE_LABELS.get(item.type, item.type.value)
    summary = _escape_text(f"{item.petName}: {item.name}")
    description = label if not item.description else f"{label}\n\n{item.description}"
    start = datetime.fromtimestamp(int(item.schedule), UTC)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{item.id}@petcare",
        f"DTSTAMP:{_format_utc(now)}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTEND:{(start + _EVENT_LENGTH).strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{_escape_text(description)}",
        f"CATEGORIES:{_escape_text(label)}",
    ]
    rule = _RRULES.get(item.period)
    if rule is not None:
        lines.append(f"RRULE:{rule}")
    if alarm_minutes > 0:
        lines.extend(
            [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:{summary}",
                f"TRIGGER:-PT{alarm_minutes}M",
                "END:VALARM",
            ]
        )
    lines.append("END:VEVENT")
    return lines


def _format_utc(moment: float) -> str:
    return datetime.fromtimestamp(int(moment), UTC).strftime("%Y%m%dT%H%M%SZ")


def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def _fold(line: str) -> str:
    data = line.encode("utf-8")
    if len(data) <= _MAX_OCTETS:
        return line
    parts: list[str] = []
    start = 0
    limit = _MAX_OCTETS
    while start < len(data):
        end = min(start + limit, len(data))
        if end < len(data):
            while end > start and (data[end] & 0xC0) == 0x80:
                end -= 1
            if end == start:
                end = start + 1
                while end < len(data) and (data[end] & 0xC0) == 0x80:
                    end += 1
        parts.append(data[start:end].decode("utf-8"))
        start = end
        limit = _MAX_OCTETS - 1
    return "\r\n ".join(parts)
