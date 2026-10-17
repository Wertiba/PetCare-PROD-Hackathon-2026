from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.database_health import DatabaseHealth
from app.application.ports.unit_of_work import UnitOfWork
from app.infra.database.db_helper import DatabaseHelper, db_helper
from app.infra.database.health import SqlAlchemyDatabaseHealth
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def database(self) -> AsyncIterator[DatabaseHelper]:
        try:
            yield db_helper
        finally:
            await db_helper.dispose()

    @provide(scope=Scope.REQUEST)
    async def session(self, database: DatabaseHelper) -> AsyncIterator[AsyncSession]:
        async with database.session_factory() as session:
            try:
                yield session
            finally:
                if session.in_transaction():
                    await session.rollback()

    unit_of_work = provide(SqlAlchemyUnitOfWork, provides=UnitOfWork, scope=Scope.REQUEST)
    health = provide(SqlAlchemyDatabaseHealth, provides=DatabaseHealth, scope=Scope.REQUEST)
