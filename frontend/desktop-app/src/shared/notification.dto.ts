// Фрагмент frontend/src/entities/notification/api/notification.dto.ts
import { Uid } from './global.types';
import {
  Notification,
  NotificationStatus,
} from './notification.types';

export interface FetchNotificationsReqDto {
  page: number;
  size: number;
  eventId?: Uid;
  petId?: Uid;
  status?: NotificationStatus;
  due?: boolean;
}

export interface FetchNotificationsResDto {
  items: Notification[];
  page: number;
  size: number;
  total: number;
}
