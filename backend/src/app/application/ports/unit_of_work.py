from typing import Protocol

from app.domain.animals.entity import Animal
from app.domain.breeds.entity import Breed
from app.domain.categories.entity import Category
from app.domain.events.entity import Event
from app.domain.foods.entity import Food
from app.domain.notes.entity import Note
from app.domain.notifications.entity import Notification
from app.domain.pets.entity import Pet
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.states.entity import State
from app.domain.users.entity import User

type Entity = User | Animal | Breed | Pet | Category | State | Event | Notification | Note | Food | RefreshToken


class UnitOfWork(Protocol):
    async def add(self, entity: Entity) -> None: ...
    async def delete(self, entity: Entity) -> None: ...
    async def commit(self) -> None: ...
