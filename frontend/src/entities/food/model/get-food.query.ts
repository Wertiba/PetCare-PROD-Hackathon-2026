import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchFoods } from '../api';
import type { FetchFoodsReqDto } from '../api';

export const useGetFoodsQuery = (query: FetchFoodsReqDto) =>
  useQuery({
    queryKey: [...queryKeys.foods.all, query],
    queryFn: () => fetchFoods(query),
  });
