from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query

from app.core.schemas.state import StateFilterQuery, StateSummaryQuery
from app.core.utils import as_aware_utc


def _utc(value: datetime | None) -> datetime | None:
    return as_aware_utc(value) if value is not None else None


def get_state_filters(
    petId: UUID | None = Query(None),
    catId: UUID | None = Query(None),
    from_: datetime | None = Query(None, alias="from", description="Inclusive lower bound of `time`"),
    to: datetime | None = Query(None, description="Inclusive upper bound of `time`"),
) -> StateFilterQuery:
    return StateFilterQuery(petId=petId, catId=catId, from_=_utc(from_), to=_utc(to))


def get_state_summary_query(
    petId: UUID = Query(...),
    catId: UUID = Query(...),
    from_: datetime | None = Query(None, alias="from", description="Inclusive lower bound of `time`"),
    to: datetime | None = Query(None, description="Inclusive upper bound of `time`"),
) -> StateSummaryQuery:
    return StateSummaryQuery(petId=petId, catId=catId, from_=_utc(from_), to=_utc(to))


StateFilterDep = Annotated[StateFilterQuery, Depends(get_state_filters)]
StateSummaryDep = Annotated[StateSummaryQuery, Depends(get_state_summary_query)]
