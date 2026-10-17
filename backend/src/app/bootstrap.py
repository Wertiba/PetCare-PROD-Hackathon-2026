from dishka import AsyncContainer, Provider, make_async_container

from app.application.animals.di import AnimalProvider
from app.application.auth.di import AuthProvider
from app.application.breeds.di import BreedProvider
from app.application.categories.di import CategoryProvider
from app.application.events.di import EventProvider
from app.application.foods.di import FoodProvider
from app.application.notes.di import NoteProvider
from app.application.notifications.di import NotificationProvider
from app.application.pets.di import PetProvider
from app.application.reports.di import ReportProvider
from app.application.states.di import StateProvider
from app.application.users.di import UserProvider
from app.infra.avatars.di import AvatarProvider
from app.infra.database.di import DatabaseProvider
from app.infra.gateways.di import GatewayProvider
from app.infra.photos.di import PhotoProvider
from app.infra.reports.di import ReportRendererProvider
from app.infra.security.di import SecurityProvider


def build_container(*overrides: Provider) -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        GatewayProvider(),
        SecurityProvider(),
        PhotoProvider(),
        AvatarProvider(),
        ReportRendererProvider(),
        AuthProvider(),
        UserProvider(),
        PetProvider(),
        AnimalProvider(),
        BreedProvider(),
        CategoryProvider(),
        StateProvider(),
        EventProvider(),
        NotificationProvider(),
        NoteProvider(),
        FoodProvider(),
        ReportProvider(),
        *overrides,
    )
