import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import { fetchCategories } from '../api';
import type { FetchCategoriesReqDto } from '../api';

export const useGetCategoriesQuery = (
  query: FetchCategoriesReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.categories.all, query],
    queryFn: () => fetchCategories(query),
  });
