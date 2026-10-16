from typing import Annotated

from fastapi import Depends, Query

from app.core.enums import CategoryType
from app.core.schemas.category import CategoryFilterQuery


def get_category_filters(
    type: CategoryType | None = Query(None),
    q: str | None = Query(None, description="Substring of the category name"),
) -> CategoryFilterQuery:
    return CategoryFilterQuery(type=type, q=q)


CategoryFilterDep = Annotated[CategoryFilterQuery, Depends(get_category_filters)]
