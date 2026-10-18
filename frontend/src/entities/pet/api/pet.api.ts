import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { Animal, Breed, Pet } from '../model';
import {
  CreateAnimalReqDto,
  CreateBreedReqDto,
  CreatePetReqDto,
  FetchAnimalsReqDto,
  FetchAnimalsResDto,
  FetchBreedsReqDto,
  FetchBreedsResDto,
  FetchPetsReqDto,
  FetchPetsResDto,
  UpdateAnimalReqDto,
  UpdateBreedReqDto,
  UpdatePetReqDto,
} from './pet.dto';

export const fetchPets = async (query: FetchPetsReqDto) =>
  (
    await api.get<FetchPetsResDto>('/pets', {
      params: query,
    })
  ).data;

export const fetchPetById = async (petId: Uid) =>
  (await api.get<Pet>(`/pets/${petId}`)).data;

export const createPet = async (pet: CreatePetReqDto) =>
  (await api.post<Pet>('/pets', pet)).data;

export const updatePet = async (
  petId: Uid,
  pet: UpdatePetReqDto,
) => (await api.patch<Pet>(`/pets/${petId}`, pet)).data;

export const deletePet = async (petId: Uid) =>
  (await api.delete<void>(`/pets/${petId}`)).data;

/** Uploading a new file replaces the pet's only photo on the server. */
export const uploadPetPhoto = async (
  petId: Uid,
  file: File,
) => {
  const data = new FormData();
  data.append('file', file);

  return (
    await api.put<Pet>(`/pets/${petId}/photo`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  ).data;
};

export const generatePetAvatar = async (petId: Uid) =>
  (await api.post<Pet>(`/pets/${petId}/avatar/generate`))
    .data;

export const selectPetAvatar = async (
  petId: Uid,
  source: Pet['avatarSource'],
) =>
  (
    await api.put<Pet>(`/pets/${petId}/avatar`, {
      source,
    })
  ).data;

export const fetchBreeds = async (
  query: FetchBreedsReqDto,
) =>
  (
    await api.get<FetchBreedsResDto>('/breeds', {
      params: query,
    })
  ).data;

export const fetchAnimals = async (
  query: FetchAnimalsReqDto,
) =>
  (
    await api.get<FetchAnimalsResDto>('/animals', {
      params: query,
    })
  ).data;

export const createAnimal = async (
  animal: CreateAnimalReqDto,
) => (await api.post<Animal>('/animals', animal)).data;

export const updateAnimal = async (
  animalId: Uid,
  animal: UpdateAnimalReqDto,
) =>
  (await api.patch<Animal>(`/animals/${animalId}`, animal))
    .data;

export const deleteAnimal = async (animalId: Uid) =>
  (await api.delete<void>(`/animals/${animalId}`)).data;

export const createBreed = async (
  breed: CreateBreedReqDto,
) => (await api.post<Breed>('/breeds', breed)).data;

export const updateBreed = async (
  breedId: Uid,
  breed: UpdateBreedReqDto,
) =>
  (await api.patch<Breed>(`/breeds/${breedId}`, breed))
    .data;

export const deleteBreed = async (breedId: Uid) =>
  (await api.delete<void>(`/breeds/${breedId}`)).data;
