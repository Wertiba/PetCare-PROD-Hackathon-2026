from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from app.application.ports.photos import PhotosGateway
from app.infra.config import S3Config
from app.infra.photos.s3 import S3PhotosGateway, create_s3_client


class PhotoProvider(Provider):
    @provide(scope=Scope.APP)
    async def photos(self, s3_config: S3Config) -> AsyncIterator[PhotosGateway]:
        async with create_s3_client(s3_config) as client, create_s3_client(s3_config, public=True) as signer:
            yield S3PhotosGateway(client, signer, s3_config)
