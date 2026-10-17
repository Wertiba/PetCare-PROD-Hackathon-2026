import {
  UpdateCategoryReqDto,
  updateCategory,
} from '@src/entities/category/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdateCategoryMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateCategoryReqDto;
    }) => updateCategory(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.categories.all,
      }),
  });
};
