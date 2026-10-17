import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import { Animal, Breed, Pet } from '../model';

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
  breedId: Uid;
  name: string;
  birthDate: Timestamp;
}

export interface FetchAnimalsReqDto {
  page: number;
  size: number;
  q: string;
}

export interface FetchAnimalsResDto {
  items: Animal[];
  page: number;
  size: number;
  total: number;
}

export interface FetchBreedsReqDto {
  page: number;
  size: number;
  animalId: Uid;
  q: string;
}

export interface FetchBreedsResDto {
  items: Breed[];
  page: number;
  size: number;
  total: number;
}

export interface UpdatePetReqDto {
  name?: string;
  breedId?: Uid;
  birthDate?: Timestamp;
}
