import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { Pet } from '../model';
import {
  CreatePetReqDto,
  FetchAnimalsReqDto,
  FetchAnimalsResDto,
  FetchBreedsReqDto,
  FetchBreedsResDto,
  FetchPetsReqDto,
  FetchPetsResDto,
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
