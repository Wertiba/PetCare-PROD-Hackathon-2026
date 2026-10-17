from dishka import Provider, Scope, provide

from app.application.ports.avatar_generator import AvatarGenerator
from app.infra.avatars.spirit import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    DEFAULT_TOOL_MODEL,
    SpiritAvatarGenerator,
)
from app.infra.config import setting_text


def build_avatar_generator() -> SpiritAvatarGenerator:
    return SpiritAvatarGenerator(
        base_url=setting_text("LLM_PROXY_URL") or DEFAULT_BASE_URL,
        api_key=setting_text("LLM_PROXY_API_KEY"),
        model=setting_text("LLM_AVATAR_MODEL") or DEFAULT_MODEL,
        tool_model=setting_text("LLM_IMAGE_TOOL_MODEL") or DEFAULT_TOOL_MODEL,
        timeout=float(setting_text("LLM_AVATAR_TIMEOUT") or str(DEFAULT_TIMEOUT)),
    )


class AvatarProvider(Provider):
    @provide(scope=Scope.APP)
    def avatars(self) -> AvatarGenerator:
        return build_avatar_generator()
