import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export type EventStatus =
  'planned' | 'skipped' | 'done' | 'cancelled';
export type EventPeriod =
  | 'none'
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'quarterly'
  | 'half_year'
  | 'yearly';

export interface Event {
  id: Uid;
  petId: Uid;
  name: string;
  status: EventStatus;
  schedule: Timestamp;
  period: EventPeriod;
}
