from dishka import AsyncContainer, make_async_container

from app.application.auth.di import AuthProvider
from app.application.breeds.di import BreedProvider
from app.application.categories.di import CategoryProvider
from app.application.events.di import EventProvider
from app.application.notifications.di import NotificationProvider
from app.application.pets.di import PetProvider
from app.application.states.di import StateProvider
from app.application.users.di import UserProvider
from app.infra.database.di import DatabaseProvider
from app.infra.gateways.di import GatewayProvider
from app.infra.photos.di import PhotoProvider
from app.infra.security.di import SecurityProvider


def build_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        GatewayProvider(),
        SecurityProvider(),
        PhotoProvider(),
        AuthProvider(),
        UserProvider(),
        PetProvider(),
        BreedProvider(),
        CategoryProvider(),
        StateProvider(),
        EventProvider(),
        NotificationProvider(),
    )
