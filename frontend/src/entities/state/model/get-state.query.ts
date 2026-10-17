import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchStates } from '../api';
import type { FetchStatesReqDto } from '../api';

export const useGetStatesQuery = (
  query: FetchStatesReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.states.all, query],
    queryFn: () => fetchStates(query),
  });
