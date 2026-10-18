from app.domain.errors import EntityError


class NotificationNotFoundError(EntityError):
    pass


class WebPushNotConfiguredError(EntityError):
    pass


class WebPushSubscriptionGoneError(EntityError):
    pass


class WebPushEndpointRequiredError(EntityError):
    pass


class WebPushEndpointNotAllowedError(EntityError):
    pass
