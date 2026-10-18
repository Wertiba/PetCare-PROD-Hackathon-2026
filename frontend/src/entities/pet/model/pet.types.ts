import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export interface Pet {
  id: Uid;
  userId: Uid;
  name: string;
  animal: PetAnimal | null;
  breed: PetBreed | null;
  birthDate: Timestamp | null;
  ageMonths: number | null;
  photoUrl: string | null;
  generatedAvatarUrl: string | null;
  avatarSource: 'photo' | 'generated';
  avatarUrl: string | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface PetAnimal {
  id: Uid;
  name: string;
}

export interface PetBreed {
  id: Uid;
  name: string;
}

export interface Animal {
  id: Uid;
  name: string;
  createdBy: Uid | null;
  createdAt: Timestamp;
}

export interface Breed {
  id: Uid;
  animalId: Uid;
  name: string;
  createdBy: Uid | null;
  createdAt: Timestamp;
}
