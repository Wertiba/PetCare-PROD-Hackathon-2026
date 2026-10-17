import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchNotificationsReqDto,
  fetchNotificationById,
  fetchNotifications,
} from '../api';

export const useGetNotificationQuery = (
  query: FetchNotificationsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.notifications.all, query],
    queryFn: () => fetchNotifications(query),
  });

export const useGetNotificationByIdQuery = (id: Uid) =>
  useQuery({
    queryKey: [...queryKeys.notifications.all, id],
    queryFn: () => fetchNotificationById(id),
  });
