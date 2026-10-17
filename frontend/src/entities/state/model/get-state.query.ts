import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchStatesReqDto,
  fetchStateById,
  fetchStates,
} from '../api';

export const useGetStatesQuery = (
  query: FetchStatesReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.states.all, query],
    queryFn: () => fetchStates(query),
  });

export const useGetStateByIdQuery = (id: Uid) =>
  useQuery({
    queryKey: [...queryKeys.states.all, id],
    queryFn: () => fetchStateById(id),
  });
