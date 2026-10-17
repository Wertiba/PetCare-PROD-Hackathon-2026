import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchNotifications } from '../api';
import type { FetchNotificationsReqDto } from '../api';

export const useGetNotificationsQuery = (
  query: FetchNotificationsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.notifications.all, query],
    queryFn: () => fetchNotifications(query),
  });
