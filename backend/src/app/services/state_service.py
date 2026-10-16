from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.enums import CategoryType
from app.core.exceptions.category_exs import RelatedCategoryNotFoundError
from app.core.exceptions.pet_exs import RelatedPetNotFoundError
from app.core.exceptions.state_exs import InvalidStateValueError, StateNotFoundError
from app.core.logger import Logger
from app.core.metrics import track
from app.core.schemas.state import (
    StateCreateBody,
    StateFilterQuery,
    StateReadResponse,
    StateSummaryQuery,
    StateSummaryResponse,
    StateUpdateBody,
)
from app.core.utils import as_aware_utc
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Category, State
from app.infrastructure.unit_of_work import UnitOfWork

logger = Logger.get_logger()

SCALE_MIN = 1
SCALE_MAX = 5


def validate_state_value(category_type: CategoryType, value: int) -> None:
    """check is a 0/1 flag, scale is a 1..5 score, number is any non-negative amount."""
    if category_type == CategoryType.CHECK and value not in {0, 1}:
        raise InvalidStateValueError("Value must be 0 or 1 for a check category", value)
    if category_type == CategoryType.SCALE and not SCALE_MIN <= value <= SCALE_MAX:
        raise InvalidStateValueError(f"Value must be between {SCALE_MIN} and {SCALE_MAX} for a scale category", value)
    if category_type == CategoryType.NUMBER and value < 0:
        raise InvalidStateValueError("Value must not be negative", value)


class StateService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(state: State) -> StateReadResponse:
        return StateReadResponse(
            id=state.id,
            petId=state.pet_id,
            catId=state.cat_id,
            value=state.value,
            note=state.note,
            time=state.time,
            createdAt=state.created_at,
        )

    async def _require_pet(self, user_id: UUID, pet_id: UUID) -> None:
        if await self.uow.pet_repo.get_for_user(pet_id, user_id) is None:
            raise RelatedPetNotFoundError

    async def _require_category(self, user_id: UUID, cat_id: UUID) -> Category:
        category = await self.uow.category_repo.get_visible(cat_id, user_id)
        if category is None:
            raise RelatedCategoryNotFoundError
        return category

    async def _require_state(self, user_id: UUID, state_id: UUID) -> State:
        state = await self.uow.state_repo.get_for_user(state_id, user_id)
        if state is None:
            raise StateNotFoundError
        return state

    async def list_states(
        self, user_id: UUID, pagination: PaginationParams, filters: StateFilterQuery
    ) -> Page[StateReadResponse]:
        async with self.uow:
            states = await self.uow.state_repo.list_for_user(
                user_id, filters, offset=pagination.offset, limit=pagination.limit
            )
            total = await self.uow.state_repo.count_for_user(user_id, filters)
            items = [self._to_read_response(state) for state in states]
            return Page.build(items=items, total=total, pagination=pagination)

    async def get_state(self, user_id: UUID, state_id: UUID) -> StateReadResponse:
        async with self.uow:
            return self._to_read_response(await self._require_state(user_id, state_id))

    async def create_state(self, user_id: UUID, data: StateCreateBody) -> StateReadResponse:
        async with self.uow:
            await self._require_pet(user_id, data.petId)
            category = await self._require_category(user_id, data.catId)
            validate_state_value(category.type, data.value)
            state = await self.uow.state_repo.add(
                State(
                    pet_id=data.petId,
                    cat_id=data.catId,
                    value=data.value,
                    note=data.note,
                    time=data.time or datetime.now(UTC),
                )
            )
            logger.info("State {} recorded for pet {} in category {}", state.id, data.petId, category.name)
            track("state", "created")
            return self._to_read_response(state)

    async def update_state(self, user_id: UUID, state_id: UUID, data: StateUpdateBody) -> StateReadResponse:
        async with self.uow:
            state = await self._require_state(user_id, state_id)
            provided = data.model_dump(exclude_unset=True)
            values: dict[str, Any] = {}
            if "value" in provided:
                category = await self.uow.category_repo.get_by_id(state.cat_id)
                if category is not None:
                    validate_state_value(category.type, provided["value"])
                values["value"] = provided["value"]
            if "time" in provided:
                values["time"] = provided["time"]
            if "note" in provided:
                values["note"] = provided["note"]
            if not values:
                return self._to_read_response(state)
            await self.uow.state_repo.update(state.id, values)
            return self._to_read_response(await self._require_state(user_id, state_id))

    async def delete_state(self, user_id: UUID, state_id: UUID) -> None:
        async with self.uow:
            state = await self._require_state(user_id, state_id)
            await self.uow.state_repo.delete(state)
            track("state", "deleted")

    async def summarize(self, user_id: UUID, query: StateSummaryQuery) -> StateSummaryResponse:
        """Aggregate a pet's states of one category the way the category kind says (sum, avg, last...)."""
        async with self.uow:
            await self._require_pet(user_id, query.petId)
            category = await self._require_category(user_id, query.catId)
            from_ = as_aware_utc(query.from_) if query.from_ else None
            to = as_aware_utc(query.to) if query.to else None
            value, count = await self.uow.state_repo.aggregate(query.petId, query.catId, category.kind, from_, to)
            return StateSummaryResponse(
                petId=query.petId,
                catId=query.catId,
                kind=category.kind,
                unit=category.unit,
                value=value,
                count=count,
                from_=from_,
                to=to,
            )
