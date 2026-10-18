from os import environ as env

from dishka import Provider, Scope, provide

from app.infra.config import (
    AppConfig,
    AvatarConfig,
    DatabaseConfig,
    HttpConfig,
    LoggingConfig,
    NotificationsConfig,
    RunConfig,
    RustFSAdminConfig,
    S3Config,
    SecurityConfig,
    WebPushConfig,
)
from app.infra.logger import Logger


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_app(self) -> AppConfig:
        return AppConfig(**env)

    @provide
    def get_run(self) -> RunConfig:
        return RunConfig(**env)

    @provide
    def get_database(self) -> DatabaseConfig:
        return DatabaseConfig(**env)

    @provide
    def get_security(self) -> SecurityConfig:
        return SecurityConfig(**env)

    @provide
    def get_http(self) -> HttpConfig:
        return HttpConfig(**env)

    @provide
    def get_logging(self) -> LoggingConfig:
        return LoggingConfig(**env)

    @provide
    def s3_config(self) -> S3Config:
        return S3Config(**env)

    @provide
    def get_rustfs_admin(self) -> RustFSAdminConfig:
        return RustFSAdminConfig(**env)

    @provide
    def get_avatar(self) -> AvatarConfig:
        return AvatarConfig(**env)

    @provide
    def get_web_push(self) -> WebPushConfig:
        return WebPushConfig(**env)

    @provide
    def get_notifications(self) -> NotificationsConfig:
        return NotificationsConfig(**env)

    logger = provide(Logger)
