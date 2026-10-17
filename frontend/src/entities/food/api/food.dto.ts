import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export interface Food {
  id: Uid;
  petId: Uid;
  name: string;
  weight: number | null;
  ingredients: string[] | null;
  isApproach: boolean | null;
  isTolerability: boolean | null;
  consequences: string | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface FetchFoodsReqDto {
  page: number;
  size: number;
  petId?: Uid;
  isApproach?: boolean;
  isTolerability?: boolean;
}

export interface FetchFoodsResDto {
  items: Food[];
  page: number;
  size: number;
  total: number;
}
