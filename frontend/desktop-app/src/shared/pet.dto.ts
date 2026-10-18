// Фрагмент frontend/src/entities/pet/api/pet.dto.ts
import { Pet } from './pet.types';

export interface FetchPetsReqDto {
  page: number;
  size: number;
}

export interface FetchPetsResDto {
  items: Pet[];
  page: number;
  size: number;
  total: number;
}
