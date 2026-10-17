from dishka import Provider, Scope, provide

from app.application.ports.avatar_generator import AvatarGenerator
from app.infra.avatars.spirit import SpiritAvatarGenerator
from app.infra.config import AvatarConfig


class AvatarProvider(Provider):
    @provide(scope=Scope.APP)
    def avatars(self, config: AvatarConfig) -> AvatarGenerator:
        return SpiritAvatarGenerator(
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            tool_model=config.tool_model,
            timeout=config.timeout,
        )
