import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchPetsReqDto,
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
