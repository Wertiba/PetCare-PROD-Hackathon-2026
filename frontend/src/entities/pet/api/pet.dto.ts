import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import { Breed, Pet, PetType } from '../model';

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

export interface CreatePetReqDto {
  type: PetType;
  breedId: Uid;
  name: string;
  birthDate: Timestamp;
}

export interface FetchBreedsReqDto {
  page: number;
  size: number;
}

export interface FetchBreedsResDto {
  items: Breed[];
  page: number;
  size: number;
  total: number;
}

export interface UpdatePetReqDto {
  name?: string;
  type?: PetType;
  breedId?: Uid;
  birthDate?: Timestamp;
}
