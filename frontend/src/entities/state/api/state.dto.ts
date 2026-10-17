import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import { State } from '../model';

export interface FetchStatesReqDto {
  page: number;
  size: number;
  petId?: Uid;
  catId?: Uid;
}

export interface FetchStatesResDto {
  items: State[];
  page: number;
  size: number;
  total: number;
}

export interface CreateStateReqDto {
  petId: Uid;
  catId: Uid;
  value: number;
  time: Timestamp;
}

export interface UpdateStateReqDto {
  value?: number;
  time?: Timestamp;
  note?: string;
}
