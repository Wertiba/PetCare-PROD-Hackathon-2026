from dataclasses import dataclass


@dataclass(kw_only=True)
class Token:
    accessToken: str
    expiresIn: int


@dataclass(kw_only=True)
class AccessTokenResult:
    accessToken: str
    expiresIn: int
