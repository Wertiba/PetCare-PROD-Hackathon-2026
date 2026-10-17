from dishka import Provider, Scope, provide_all

from app.application.foods.interactors import (
    CreateFood,
    DeleteFood,
    FindSuspectIngredients,
    GetFood,
    ListFoods,
    UpdateFood,
)


class FoodProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListFoods, GetFood, CreateFood, UpdateFood, DeleteFood, FindSuspectIngredients)
