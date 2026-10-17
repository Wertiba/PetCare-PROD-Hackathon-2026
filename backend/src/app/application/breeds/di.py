from dishka import Provider, Scope, provide_all

from app.application.breeds.interactors import ListBreeds


class BreedProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListBreeds)
