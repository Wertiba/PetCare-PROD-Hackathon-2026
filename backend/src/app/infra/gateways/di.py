from dishka import Provider, Scope, provide

from app.application.ports.animal_gateway import AnimalGateway
from app.application.ports.breed_gateway import BreedGateway
from app.application.ports.category_gateway import CategoryGateway
from app.application.ports.event_gateway import EventGateway
from app.application.ports.food_gateway import FoodGateway
from app.application.ports.note_gateway import NoteGateway
from app.application.ports.notification_gateway import NotificationGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.refresh_token_gateway import RefreshTokenGateway
from app.application.ports.state_gateway import StateGateway
from app.application.ports.user_gateway import UserGateway
from app.infra.gateways.animal import SqlAlchemyAnimalGateway
from app.infra.gateways.breed import SqlAlchemyBreedGateway
from app.infra.gateways.category import SqlAlchemyCategoryGateway
from app.infra.gateways.event import SqlAlchemyEventGateway
from app.infra.gateways.food import SqlAlchemyFoodGateway
from app.infra.gateways.note import SqlAlchemyNoteGateway
from app.infra.gateways.notification import SqlAlchemyNotificationGateway
from app.infra.gateways.pet import SqlAlchemyPetGateway
from app.infra.gateways.refresh_token import SqlAlchemyRefreshTokenGateway
from app.infra.gateways.state import SqlAlchemyStateGateway
from app.infra.gateways.user import SqlAlchemyUserGateway


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    user = provide(SqlAlchemyUserGateway, provides=UserGateway)
    animal = provide(SqlAlchemyAnimalGateway, provides=AnimalGateway)
    breed = provide(SqlAlchemyBreedGateway, provides=BreedGateway)
    pet = provide(SqlAlchemyPetGateway, provides=PetGateway)
    category = provide(SqlAlchemyCategoryGateway, provides=CategoryGateway)
    state = provide(SqlAlchemyStateGateway, provides=StateGateway)
    event = provide(SqlAlchemyEventGateway, provides=EventGateway)
    notification = provide(SqlAlchemyNotificationGateway, provides=NotificationGateway)
    note = provide(SqlAlchemyNoteGateway, provides=NoteGateway)
    food = provide(SqlAlchemyFoodGateway, provides=FoodGateway)
    refresh_token = provide(SqlAlchemyRefreshTokenGateway, provides=RefreshTokenGateway)
