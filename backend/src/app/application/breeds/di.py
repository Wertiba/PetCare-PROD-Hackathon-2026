from dishka import Provider, Scope, provide_all

from app.application.breeds.interactors import CreateBreed, DeleteBreed, GetBreed, ListBreeds, UpdateBreed


class BreedProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListBreeds, GetBreed, CreateBreed, UpdateBreed, DeleteBreed)
