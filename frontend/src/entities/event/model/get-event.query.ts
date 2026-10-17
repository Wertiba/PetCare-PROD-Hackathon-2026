import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchEvents } from '../api';
import type { FetchEventsReqDto } from '../api';

export const useGetEventsQuery = (
  query: FetchEventsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.events.all, query],
    queryFn: () => fetchEvents(query),
  });
