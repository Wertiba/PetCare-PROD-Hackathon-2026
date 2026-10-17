import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.domain.users.errors import InvalidCredentialsError
from app.infra.config import SecurityConfig
from app.infra.duration import parse_duration_seconds

ACCESS_TOKEN_TYPE = "access"  # noqa: S105 -- JWT "type" claim discriminator, not a credential
REFRESH_TOKEN_TYPE = "refresh"  # noqa: S105 -- JWT "type" claim discriminator, not a credential


class JWTService:
    def __init__(self, config: SecurityConfig):
        self._dummy_password_hash: str | None = None
        self.pwd_context = CryptContext(schemes=[config.password_scheme], deprecated="auto")
        self.secret_key = config.jwt_secret
        self.algorithm = config.algorithm
        self.access_expire_seconds = parse_duration_seconds(config.access_token_expiration)
        self.refresh_expire_seconds = parse_duration_seconds(config.refresh_token_expiration)

    def verify_dummy_password(self, password: str) -> None:
        if self._dummy_password_hash is None:
            self._dummy_password_hash = self.get_password_hash("dummy-password-for-timing")
        self.verify_password(password, self._dummy_password_hash)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def _create_token(self, subject: str, token_type: str, expire_seconds: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "type": token_type,
            "jti": str(uuid.uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expire_seconds)).timestamp()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, subject: str) -> str:
        return self._create_token(subject, ACCESS_TOKEN_TYPE, self.access_expire_seconds)

    def create_refresh_token(self, subject: str) -> str:
        return self._create_token(subject, REFRESH_TOKEN_TYPE, self.refresh_expire_seconds)

    def decode_token(self, token: str, expected_type: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.InvalidTokenError as e:
            raise InvalidCredentialsError from e

        if payload.get("sub") is None or payload.get("type") != expected_type:
            raise InvalidCredentialsError
        return payload

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
