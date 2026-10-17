from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.notes.dto import NoteCreateData, NoteUpdateData
from app.application.notes.interactors import CreateNote, DeleteNote, GetNote, ListNotes, UpdateNote
from app.application.pagination import Pagination
from app.domain.notes.ids import NoteId
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.note import NoteCreateBody, NoteReadResponse, NoteUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/notes", tags=["Notes"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Note not found"}}
_UNPROCESSABLE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Pet not found"}}


@router.get("", response_model=Page[NoteReadResponse], status_code=status.HTTP_200_OK)
async def list_notes(
    user: CurrentUserDep,
    interactor: FromDishka[ListNotes],
    pagination: PaginationDep,
    petId: PetId | None = Query(None),
    q: str | None = Query(None, description="Substring of the note text"),
) -> Page[NoteReadResponse]:
    """Newest first."""
    return Page[NoteReadResponse].model_validate(
        await interactor(user.id, Pagination(page=pagination.page, size=pagination.size), pet_id=petId, query=q),
        from_attributes=True,
    )


@router.post("", response_model=NoteReadResponse, status_code=status.HTTP_201_CREATED, responses=_UNPROCESSABLE)
async def create_note(
    user: CurrentUserDep, interactor: FromDishka[CreateNote], body: NoteCreateBody, response: Response
) -> NoteReadResponse:
    created = await interactor(user.id, NoteCreateData(**body.model_dump()))
    track("note", "created")
    response.headers["Location"] = f"/api/v1/notes/{created.id}"
    return NoteReadResponse.model_validate(created, from_attributes=True)


@router.get("/{note_id}", response_model=NoteReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_note(user: CurrentUserDep, note_id: NoteId, interactor: FromDishka[GetNote]) -> NoteReadResponse:
    return NoteReadResponse.model_validate(await interactor(user.id, note_id), from_attributes=True)


@router.patch("/{note_id}", response_model=NoteReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def update_note(
    user: CurrentUserDep, note_id: NoteId, interactor: FromDishka[UpdateNote], body: NoteUpdateBody
) -> NoteReadResponse:
    return NoteReadResponse.model_validate(
        await interactor(user.id, note_id, NoteUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete("/{note_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_note(user: CurrentUserDep, note_id: NoteId, interactor: FromDishka[DeleteNote]) -> None:
    await interactor(user.id, note_id)
    track("note", "deleted")
