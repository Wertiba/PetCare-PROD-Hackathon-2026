from app.domain.errors import EntityError


class CategoryNotFoundError(EntityError):
    pass


class RelatedCategoryNotFoundError(EntityError):
    """categoryId in a request body points to a category the user cannot see."""


class SystemCategoryReadOnlyError(EntityError):
    pass


class CategoryInUseError(EntityError):
    """Other users already record states in the category, so it cannot be deleted or reinterpreted."""
