from dishka import Provider, Scope, provide

from app.application.ports.web_push import WebPushSender
from app.infra.config import WebPushConfig
from app.infra.webpush.sender import PyWebPushSender


class WebPushProvider(Provider):
    @provide(scope=Scope.APP)
    def sender(self, config: WebPushConfig) -> WebPushSender:
        return PyWebPushSender(config)
