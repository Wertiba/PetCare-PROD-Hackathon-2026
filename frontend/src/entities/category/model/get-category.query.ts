import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import { useQuery } from '@tanstack/react-query';

import {
  FetchCategoriesReqDto,
  fetchCategories,
  fetchCategoryById,
} from '../api';

export const useGetCategoriesQuery = (
  query: FetchCategoriesReqDto,
) =>
  useQuery({
    queryKey: [...queryKeys.categories.all, query],
    queryFn: () => fetchCategories(query),
  });

export const useGetCategoryByIdQuery = (id: Uid) =>
  useQuery({
    queryKey: [...queryKeys.categories.all, id],
    queryFn: () => fetchCategoryById(id),
  });
