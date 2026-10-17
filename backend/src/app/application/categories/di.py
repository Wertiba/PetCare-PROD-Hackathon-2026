from dishka import Provider, Scope, provide_all

from app.application.categories.interactors import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)


class CategoryProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListCategories, GetCategory, CreateCategory, UpdateCategory, DeleteCategory)
