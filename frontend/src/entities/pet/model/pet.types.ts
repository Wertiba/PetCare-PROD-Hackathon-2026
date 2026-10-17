import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export type PetType =
  | 'cat'
  | 'dog'
  | 'rodent'
  | 'bird'
  | 'fish'
  | 'reptile'
  | 'other';

export interface Pet {
  id: Uid;
  userId: Uid;
  type: PetType;
  breed: Breed;
  name: string;
  birthDate: Timestamp;
  createdAt: Timestamp;
}

export interface Breed {
  id: Uid;
  type: PetType;
  name: string;
}
