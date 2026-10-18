from datetime import UTC, datetime

TEST_TITLE = "Проверка уведомлений"
TEST_BODY = "Если вы видите это сообщение, канал PetCare подключён."


def reminder_parts(event_name: str, pet_name: str, when: float) -> tuple[str, str]:
    stamp = datetime.fromtimestamp(when, UTC).strftime("%d.%m.%Y %H:%M UTC")
    return f"Напоминание: {event_name}", f"{pet_name}\n{stamp}"
