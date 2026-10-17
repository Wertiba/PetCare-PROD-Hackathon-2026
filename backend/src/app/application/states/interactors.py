from dataclasses import dataclass
from time import time
from typing import Any

from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.ports.category_gateway import CategoryGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.state_gateway import StateGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.states.dto import StateCreateData, StateResult, StateSummaryResult, StateUpdateData
from app.domain.categories.entity import Category
from app.domain.categories.errors import RelatedCategoryNotFoundError
from app.domain.categories.ids import CategoryId
from app.domain.pets.errors import RelatedPetNotFoundError
from app.domain.pets.ids import PetId
from app.domain.states.entity import State
from app.domain.states.errors import StateNotFoundError
from app.domain.states.ids import StateId
from app.domain.states.rules import validate_state_value
from app.domain.users.ids import UserId


@dataclass
class _StateContext:
    uow: UnitOfWork
    state_gateway: StateGateway
    pet_gateway: PetGateway
    category_gateway: CategoryGateway

    @staticmethod
    def _to_read_response(state: State) -> StateResult:
        return StateResult(
            id=state.id,
            petId=state.pet_id,
            catId=state.cat_id,
            value=state.value,
            note=state.note,
            time=state.time,
            createdAt=state.created_at,
        )

    async def _require_pet(self, user_id: UserId, pet_id: PetId) -> None:
        if await self.pet_gateway.get_by_id(pet_id, user_id=user_id) is None:
            raise RelatedPetNotFoundError

    async def _require_category(self, cat_id: CategoryId) -> Category:
        category = await self.category_gateway.get_by_id(cat_id)
        if category is None:
            raise RelatedCategoryNotFoundError
        return category

    async def _require_state(self, user_id: UserId, state_id: StateId) -> State:
        state = await self.state_gateway.get_by_id(state_id, user_id=user_id)
        if state is None:
            raise StateNotFoundError
        return state


class ListStates(_StateContext):
    async def __call__(
        self,
        user_id: UserId,
        pagination: Pagination,
        *,
        pet_id: PetId | None = None,
        cat_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> Page[StateResult]:
        states = await self.state_gateway.get_by_user_id(
            user_id, offset=pagination.offset, limit=pagination.limit, pet_id=pet_id, cat_id=cat_id, from_=from_, to=to
        )
        total = await self.state_gateway.count_by_user_id(user_id, pet_id=pet_id, cat_id=cat_id, from_=from_, to=to)
        items = [self._to_read_response(state) for state in states]
        return Page.build(items=items, total=total, pagination=pagination)


class GetState(_StateContext):
    async def __call__(self, user_id: UserId, state_id: StateId) -> StateResult:
        return self._to_read_response(await self._require_state(user_id, state_id))


class CreateState(_StateContext):
    async def __call__(self, user_id: UserId, data: StateCreateData) -> StateResult:
        await self._require_pet(user_id, data.petId)
        category = await self._require_category(data.catId)
        validate_state_value(category.type, data.value)
        state = State(
            pet_id=data.petId,
            cat_id=data.catId,
            value=data.value,
            note=data.note,
            time=data.time if data.time is not None else time(),
        )
        await self.uow.add(state)
        result = self._to_read_response(state)
        await self.uow.commit()
        return result


class UpdateState(_StateContext):
    async def __call__(self, user_id: UserId, state_id: StateId, data: StateUpdateData) -> StateResult:
        state = await self._require_state(user_id, state_id)
        provided = data.changes
        values: dict[str, Any] = {}
        if "value" in provided:
            category = await self.category_gateway.get_by_id(state.cat_id)
            if category is not None:
                validate_state_value(category.type, provided["value"])
            values["value"] = provided["value"]
        if "time" in provided:
            values["time"] = provided["time"]
        if "note" in provided:
            values["note"] = provided["note"]
        if not values:
            result = self._to_read_response(state)
            await self.uow.commit()
            return result
        apply_changes(state, values)
        result = self._to_read_response(state)
        await self.uow.commit()
        return result


class DeleteState(_StateContext):
    async def __call__(self, user_id: UserId, state_id: StateId) -> None:
        state = await self._require_state(user_id, state_id)
        await self.uow.delete(state)
        await self.uow.commit()


class SummarizeStates(_StateContext):
    async def __call__(
        self, user_id: UserId, pet_id: PetId, cat_id: CategoryId, *, from_: float | None = None, to: float | None = None
    ) -> StateSummaryResult:
        """Aggregate a pet's states of one category the way the category kind says (sum, avg, last...)."""
        await self._require_pet(user_id, pet_id)
        category = await self._require_category(cat_id)
        value, count = await self.state_gateway.aggregate(pet_id, cat_id, category.kind, from_, to)
        return StateSummaryResult(
            petId=pet_id,
            catId=cat_id,
            kind=category.kind,
            unit=category.unit,
            value=value,
            count=count,
            from_=from_,
            to=to,
        )
