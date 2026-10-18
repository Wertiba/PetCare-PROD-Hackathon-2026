from dishka import Provider, Scope, provide_all

from app.application.notifications.delivery import SendTestNotification
from app.application.notifications.interactors import (
    CreateNotification,
    DeleteNotification,
    GetNotification,
    ListNotifications,
    UpdateNotification,
)
from app.application.notifications.settings import (
    DeleteWebPushSubscription,
    GetNotificationSettings,
    GetWebPushPublicKey,
    SaveWebPushSubscription,
    UpdateNotificationSettings,
)


class NotificationProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(
        ListNotifications,
        GetNotification,
        CreateNotification,
        UpdateNotification,
        DeleteNotification,
        GetNotificationSettings,
        UpdateNotificationSettings,
        GetWebPushPublicKey,
        SaveWebPushSubscription,
        DeleteWebPushSubscription,
        SendTestNotification,
    )
