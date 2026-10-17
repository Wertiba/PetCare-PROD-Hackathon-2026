import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

import {
  Notification,
  NotificationStatus,
  NotificationType,
} from '../model';

export interface FetchNotificationsReqDto {
  page: number;
  size: number;
  eventId?: Uid;
}

export interface FetchNotificationsResDto {
  items: Notification[];
  page: number;
  size: number;
  total: number;
}

export interface CreateNotificationReqDto {
  eventId: Uid;
  type: NotificationType;
  status: NotificationStatus;
  time: Timestamp;
}

export interface UpdateNotificationReqDto {
  type?: NotificationType;
  status?: NotificationStatus;
  time?: Timestamp;
}
