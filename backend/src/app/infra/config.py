import socket
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.engine import URL


class AppConfig(BaseModel):
    name: str = Field(alias="APP_NAME", default="PetCare")


class RunConfig(BaseModel):
    host: str = Field(alias="RUN_HOST", default="0.0.0.0")  # noqa: S104 -- API listen address
    port: int = Field(alias="RUN_PORT", default=8080)


class DatabaseConfig(BaseModel):
    host: str = Field(alias="DB_HOST")
    name: str = Field(alias="DB_NAME")
    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD", repr=False)
    port: int = Field(alias="DB_PORT", default=5432)
    driver: str = Field(alias="DB_DRIVER", default="postgresql+asyncpg")
    pool_size: int = Field(alias="DB_POOL_SIZE", default=50)
    max_overflow: int = Field(alias="DB_MAX_OVERFLOW", default=10)


class SecurityConfig(BaseModel):
    jwt_secret: str = Field(alias="APP_SECURITY_JWT_SECRET", repr=False)
    access_token_expiration: str = Field(alias="APP_SECURITY_ACCESS_TOKEN_EXPIRATION", default="15m")
    refresh_token_expiration: str = Field(alias="APP_SECURITY_REFRESH_TOKEN_EXPIRATION", default="30d")
    password_scheme: str = Field(alias="APP_SECURITY_PASSWORD_SCHEME", default="argon2")
    algorithm: str = Field(alias="APP_SECURITY_ALGORITHM", default="HS256")


class SeedAdminConfig(BaseModel):
    """Admin account created by migration 0011; the frontend quick-login button uses the same credentials."""

    login: str = Field(alias="ADMIN_LOGIN")
    password: str = Field(alias="ADMIN_PASSWORD", repr=False)
    full_name: str = Field(alias="ADMIN_FULL_NAME", default="Администратор")


class HttpConfig(BaseModel):
    cookie_secure: bool = Field(alias="APP_COOKIE_SECURE", default=True)
    cors_allowed_origins: str = Field(
        alias="APP_CORS_ALLOWED_ORIGINS", default="http://localhost,http://localhost:8080"
    )


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(alias="LOG_CONSOLE_LEVEL", default="INFO")
    env: str = Field(alias="LOG_ENV", default="dev", pattern=r"^[a-z][a-z0-9_-]*$", validate_default=True)
    system: str = Field(alias="LOG_SYSTEM", default="petcare", pattern=r"^[a-z][a-z0-9_-]*$", validate_default=True)
    inst: str = Field(
        alias="LOG_INST",
        default_factory=socket.gethostname,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$",
        validate_default=True,
    )


class S3Config(BaseModel):
    endpoint_url: str = Field(alias="S3_ENDPOINT_URL")
    public_endpoint_url: str = Field(alias="S3_PUBLIC_ENDPOINT_URL")
    access_key: str = Field(alias="S3_ACCESS_KEY", repr=False)
    secret_key: str = Field(alias="S3_SECRET_KEY", repr=False)
    bucket: str = Field(alias="S3_BUCKET", default="media")
    region: str = Field(alias="S3_REGION", default="us-east-1")
    presigned_ttl: int = Field(alias="S3_PRESIGNED_TTL", default=604800)
    upload_ttl: int = Field(alias="S3_UPLOAD_TTL", default=900)


class RustFSAdminConfig(BaseModel):
    access_key: str = Field(alias="RUSTFS_ACCESS_KEY", repr=False)
    secret_key: str = Field(alias="RUSTFS_SECRET_KEY", repr=False)


class AvatarConfig(BaseModel):
    base_url: str = Field(alias="LLM_PROXY_URL", default="https://llm-proxy.spirit.t-education.com")
    api_key: str = Field(alias="LLM_PROXY_API_KEY", default="", repr=False)
    model: str = Field(alias="LLM_AVATAR_MODEL", default="openai/gpt-5.6-sol")
    tool_model: str = Field(alias="LLM_IMAGE_TOOL_MODEL", default="gpt-image-1.5")
    timeout: float = Field(alias="LLM_AVATAR_TIMEOUT", default=180.0)


class WebPushConfig(BaseModel):
    public_key: str = Field(alias="VAPID_PUBLIC_KEY", default="")
    private_key: str = Field(alias="VAPID_PRIVATE_KEY", default="", repr=False)
    subject: str = Field(alias="VAPID_SUBJECT", default="")
    allowed_hosts: str = Field(
        alias="WEB_PUSH_ALLOWED_HOSTS",
        default="fcm.googleapis.com,push.services.mozilla.com,notify.windows.com,push.apple.com",
    )
    timeout: float = Field(alias="WEB_PUSH_TIMEOUT", default=10, gt=0)

    @field_validator("subject")
    @classmethod
    def vapid_subject(cls, value: str) -> str:
        stripped = value.strip()
        if stripped and not stripped.startswith(("mailto:", "https://")):
            raise ValueError("VAPID_SUBJECT must start with mailto: or https://")
        return value

    def configured(self) -> bool:
        return bool(self.public_key.strip() and self.private_key.strip() and self.subject.strip())


class NotificationsConfig(BaseModel):
    worker_enabled: bool = Field(alias="NOTIFICATIONS_WORKER_ENABLED", default=True)
    dispatch_interval: int = Field(alias="NOTIFICATIONS_DISPATCH_INTERVAL", default=15, ge=1)
    max_lateness: int = Field(alias="NOTIFICATIONS_MAX_LATENESS", default=86400, ge=0)


def build_postgres_url(config: DatabaseConfig) -> URL:
    return URL.create(
        config.driver,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.name,
    )
