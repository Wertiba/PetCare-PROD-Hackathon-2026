from dishka import Provider, Scope, provide_all

from app.application.pets.interactors import CreatePet, DeletePet, GetPet, ListPets, SetPetPhoto, UpdatePet


class PetProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListPets, GetPet, CreatePet, UpdatePet, DeletePet, SetPetPhoto)
