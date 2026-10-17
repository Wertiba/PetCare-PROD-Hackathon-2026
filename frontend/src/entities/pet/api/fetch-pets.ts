import api from '@src/shared/api/client';

import type { Pet } from '../model';

export const fetchPets = async () =>
  (await api.get<Pet[]>('/pets')).data;

export const fetchPetById = async (petId: number) =>
  await api.get<Pet>(`/pets/${petId}`);
