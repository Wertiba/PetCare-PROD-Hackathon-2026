import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export type NotificationType =
  'app' | 'telegram' | 'web_push';
export type NotificationStatus =
  'pending' | 'sent' | 'read' | 'failed';

export interface Notification {
  id: Uid;
  eventId: Uid;
  petId: Uid;
  eventName: string;
  type: NotificationType;
  status: NotificationStatus;
  time: Timestamp;
}
