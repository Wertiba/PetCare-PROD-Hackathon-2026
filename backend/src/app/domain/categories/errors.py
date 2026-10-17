from app.domain.errors import EntityError


class CategoryNotFoundError(EntityError):
    pass


class RelatedCategoryNotFoundError(EntityError):
    """catId in a request body points to a category the user cannot see."""


class SystemCategoryReadOnlyError(EntityError):
    pass
