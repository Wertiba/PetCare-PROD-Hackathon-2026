from dataclasses import dataclass
from datetime import UTC, datetime
from time import time

from app.application.ports.category_gateway import CategoryGateway
from app.application.ports.event_gateway import EventGateway
from app.application.ports.food_gateway import FoodGateway
from app.application.ports.note_gateway import NoteGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.pet_report import PetReportRenderer
from app.application.ports.photos import PhotoStorage
from app.application.ports.state_gateway import StateGateway
from app.application.reports.builder import build_report
from app.application.reports.dto import PetReportFile
from app.domain.pets.errors import PetNotFoundError
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId

# The whole history of one pet: years of daily records stay well below this.
HISTORY_LIMIT = 10_000


@dataclass
class ExportPetReport:
    pet_gateway: PetGateway
    event_gateway: EventGateway
    state_gateway: StateGateway
    category_gateway: CategoryGateway
    food_gateway: FoodGateway
    note_gateway: NoteGateway
    photos: PhotoStorage
    renderer: PetReportRenderer

    async def __call__(self, user_id: UserId, pet_id: PetId) -> PetReportFile:
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        events = await self.event_gateway.get_by_user_id(user_id, 0, HISTORY_LIMIT, pet_id=pet_id)
        states = await self.state_gateway.get_by_user_id(user_id, 0, HISTORY_LIMIT, pet_id=pet_id)
        categories = {}
        for category_id in {state.category_id for state in states}:
            category = await self.category_gateway.get_by_id(category_id)
            if category is not None:
                categories[category_id] = category
        food_records = await self.food_gateway.get_by_user_id(user_id, 0, HISTORY_LIMIT, pet_id=pet_id)
        notes = await self.note_gateway.get_by_user_id(user_id, 0, HISTORY_LIMIT, pet_id=pet_id)
        now = time()
        report = build_report(
            pet,
            events=events,
            states=states,
            categories=categories,
            food_records=food_records,
            notes=notes,
            photo=await self.photos.load(pet.photo_key) if pet.photo_key else None,
            now=now,
        )
        day = datetime.fromtimestamp(now, UTC).strftime("%Y-%m-%d")
        return PetReportFile(filename=f"petcare-{pet.name}-{day}.pdf", content=await self.renderer.render(report))
