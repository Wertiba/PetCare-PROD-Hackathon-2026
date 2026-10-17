import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import {
  Event,
  EventPeriod,
  EventStatus,
  EventType,
} from '../model';

export interface FetchEventsReqDto {
  page: number;
  size: number;
  petId?: Uid;
  status?: EventStatus;
  type?: EventType;
  from?: Timestamp;
  to?: Timestamp;
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
  type: EventType;
  status: EventStatus;
  schedule: Timestamp;
  period: EventPeriod;
}

export interface UpdateEventReqDto {
  name?: string;
  type?: EventType;
  status?: EventStatus;
  schedule?: Timestamp;
  period?: EventPeriod;
  description?: string;
}
