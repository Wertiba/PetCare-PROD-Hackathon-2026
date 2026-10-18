// Копия frontend/src/entities/notification/model/notification.types.ts
import { Timestamp, Uid } from './global.types';

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
