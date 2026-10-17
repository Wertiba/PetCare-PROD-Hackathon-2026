import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchEventsReqDto,
  fetchEventById,
  fetchEvents,
} from '../api';

export const useGetEventQuery = (
  query: FetchEventsReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.events.all, query],
    queryFn: () => fetchEvents(query),
  });

export const useGetEventByIdQuery = (id: Uid) =>
  useQuery({
    queryKey: [...queryKeys.events.all, id],
    queryFn: () => fetchEventById(id),
  });
