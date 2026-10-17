import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import { Event, EventPeriod, EventStatus } from '../model';

export interface FetchEventsReqDto {
  page: number;
  size: number;
  petId?: Uid;
}

export interface FetchEventsResDto {
  items: Event[];
  page: number;
  size: number;
  total: number;
}

export interface CreateEventReqDto {
  petId: Uid;
  name: string;
  status: EventStatus;
  schedule: Timestamp;
  period: EventPeriod;
}

export interface UpdateEventReqDto {
  name?: string;
  status?: EventStatus;
  schedule?: Timestamp;
  period?: EventPeriod;
  description?: string;
}
