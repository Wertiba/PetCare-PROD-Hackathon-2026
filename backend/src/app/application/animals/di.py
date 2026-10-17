from dishka import Provider, Scope, provide_all

from app.application.animals.interactors import CreateAnimal, DeleteAnimal, GetAnimal, ListAnimals, UpdateAnimal


class AnimalProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListAnimals, GetAnimal, CreateAnimal, UpdateAnimal, DeleteAnimal)
