from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories import (
    BreedRepository,
    CategoryRepository,
    EventRepository,
    NotificationRepository,
    PetRepository,
    RefreshTokenRepository,
    StateRepository,
    UserRepository,
)
from app.infrastructure.unit_of_work.abstract_uow import AbstractUnitOfWork


class UnitOfWork(AbstractUnitOfWork):
    user_repo: UserRepository
    refresh_token_repo: RefreshTokenRepository
    breed_repo: BreedRepository
    pet_repo: PetRepository
    category_repo: CategoryRepository
    state_repo: StateRepository
    event_repo: EventRepository
    notification_repo: NotificationRepository

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        self.user_repo = UserRepository(self.session)
        self.refresh_token_repo = RefreshTokenRepository(self.session)
        self.breed_repo = BreedRepository(self.session)
        self.pet_repo = PetRepository(self.session)
        self.category_repo = CategoryRepository(self.session)
        self.state_repo = StateRepository(self.session)
        self.event_repo = EventRepository(self.session)
        self.notification_repo = NotificationRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
