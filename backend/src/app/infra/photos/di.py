from dishka import Provider, Scope, provide

from app.application.ports.photos import PhotoStorage
from app.infra.config import get_media_dir
from app.infra.photos.storage import LocalPhotoStorage


class PhotoProvider(Provider):
    @provide(scope=Scope.APP)
    def photos(self) -> PhotoStorage:
        return LocalPhotoStorage(get_media_dir())
