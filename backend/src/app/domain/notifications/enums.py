from enum import Enum


class NotificationType(str, Enum):
    APP = "app"
    TELEGRAM = "telegram"
    WEB_PUSH = "web_push"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"
