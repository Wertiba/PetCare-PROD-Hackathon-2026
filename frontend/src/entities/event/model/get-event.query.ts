import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchEvents, fetchUpcomingEvents } from '../api';
import type {
  FetchEventsReqDto,
  FetchUpcomingEventsReqDto,
} from '../api';

export const useGetEventsQuery = (
  query: FetchEventsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.events.all, query],
    queryFn: () => fetchEvents(query),
  });

export const useGetUpcomingEventsQuery = (
  query: FetchUpcomingEventsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.events.all, 'upcoming', query],
    queryFn: () => fetchUpcomingEvents(query),
  });
