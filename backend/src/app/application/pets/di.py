from dishka import Provider, Scope, provide_all

from app.application.pets.interactors import (
    ConfirmPetPhoto,
    CreatePet,
    DeleteGeneratedAvatar,
    DeletePet,
    DeletePetPhoto,
    GeneratePetAvatar,
    GetPet,
    IssuePetPhotoUploadUrl,
    ListPets,
    SelectPetAvatar,
    SetPetPhoto,
    UpdatePet,
)


class PetProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(
        ListPets,
        GetPet,
        CreatePet,
        UpdatePet,
        DeletePet,
        SetPetPhoto,
        IssuePetPhotoUploadUrl,
        ConfirmPetPhoto,
        DeletePetPhoto,
        GeneratePetAvatar,
        SelectPetAvatar,
        DeleteGeneratedAvatar,
    )
