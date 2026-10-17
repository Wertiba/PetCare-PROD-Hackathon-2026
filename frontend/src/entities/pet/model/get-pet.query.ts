import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchAnimalsReqDto,
  FetchBreedsReqDto,
  FetchPetsReqDto,
  fetchAnimals,
  fetchBreeds,
  fetchPetById,
  fetchPets,
} from '../api';

export const useGetPetQuery = (query: FetchPetsReqDto) =>
  useQuery({
    queryKey: [...queryKeys.pets.all, query],
    queryFn: () => fetchPets(query),
  });

export const useGetPetByIdQuery = (petId: Uid) =>
  useQuery({
    queryKey: [...queryKeys.pets.all, petId],
    queryFn: () => fetchPetById(petId),
  });

export const useGetBreedsQuery = (
  query: FetchBreedsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.breeds.all, query],
    queryFn: () => fetchBreeds(query),
  });

export const useGetAnimalsQuery = (
  query: FetchAnimalsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.animals.all, query],
    queryFn: () => fetchAnimals(query),
  });
