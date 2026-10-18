from urllib.parse import urlsplit

from pydantic import Field, field_validator

from app.domain.events.ids import EventId
from app.domain.notifications.enums import NotificationStatus, NotificationType
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId
from app.presentation.http.schemas.base import PyModel


class NotificationCreateBody(PyModel):
    eventId: EventId
    type: NotificationType = NotificationType.APP
    status: NotificationStatus = NotificationStatus.PENDING
    time: float | None = Field(
        None, description="Defaults to the event schedule. Unix seconds in UTC; fractional seconds are supported."
    )


class NotificationUpdateBody(PyModel):
    type: NotificationType | None = None
    status: NotificationStatus | None = None
    time: float | None = Field(None, description="Unix seconds in UTC; fractional seconds are supported.")

    @field_validator("type", "status", "time", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class NotificationReadResponse(PyModel):
    id: NotificationId
    eventId: EventId
    petId: PetId
    eventName: str
    type: NotificationType
    status: NotificationStatus
    time: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    deliveredAt: float | None = Field(
        None,
        description=(
            "When at least one device accepted the push, or the remaining subscriptions were all revoked. "
            "Null until then. Status is unchanged."
        ),
    )


class NotificationSettingsResponse(PyModel):
    webPushEnabled: bool
    webPushAvailable: bool


class NotificationSettingsPatchBody(PyModel):
    webPushEnabled: bool | None = None

    @field_validator("webPushEnabled", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class WebPushKeysBody(PyModel):
    p256dh: str = Field(max_length=255)
    auth: str = Field(max_length=255)

    @field_validator("p256dh", "auth")
    @classmethod
    def not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value cannot be empty")
        return stripped


class WebPushSubscriptionBody(PyModel):
    endpoint: str = Field(max_length=2048)
    keys: WebPushKeysBody
    expirationTime: float | None = None

    @field_validator("endpoint")
    @classmethod
    def https_endpoint(cls, value: str) -> str:
        stripped = value.strip()
        parsed = urlsplit(stripped)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("endpoint must be an https URL")
        return stripped


class WebPushUnsubscribeBody(PyModel):
    endpoint: str


class WebPushPublicKeyResponse(PyModel):
    publicKey: str


class ChannelDeliveryResponse(PyModel):
    channel: str
    ok: bool
    error: str | None = None


class TestNotificationResponse(PyModel):
    channels: list[ChannelDeliveryResponse]
