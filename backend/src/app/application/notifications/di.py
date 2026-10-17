from dishka import Provider, Scope, provide_all

from app.application.notifications.interactors import (
    CreateNotification,
    DeleteNotification,
    GetNotification,
    ListNotifications,
    UpdateNotification,
)


class NotificationProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(
        ListNotifications, GetNotification, CreateNotification, UpdateNotification, DeleteNotification
    )
