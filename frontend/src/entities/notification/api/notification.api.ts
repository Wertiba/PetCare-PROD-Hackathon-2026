import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { Notification } from '../model';
import {
  CreateNotificationReqDto,
  FetchNotificationsReqDto,
  FetchNotificationsResDto,
  UpdateNotificationReqDto,
} from './notification.dto';

export const fetchNotifications = async (
  query: FetchNotificationsReqDto,
) =>
  (
    await api.get<FetchNotificationsResDto>(
      '/notifications',
      {
        params: query,
      },
    )
  ).data;

export const fetchNotificationById = async (id: Uid) =>
  (await api.get<Notification>(`/notifications/${id}`))
    .data;

export const createNotification = async (
  notification: CreateNotificationReqDto,
) =>
  (
    await api.post<Notification>(
      '/notifications',
      notification,
    )
  ).data;

export const updateNotification = async (
  id: Uid,
  notification: UpdateNotificationReqDto,
) =>
  (
    await api.patch<Notification>(
      `/notifications/${id}`,
      notification,
    )
  ).data;

export const deleteNotification = async (id: Uid) =>
  (await api.delete<void>(`/notifications/${id}`)).data;
