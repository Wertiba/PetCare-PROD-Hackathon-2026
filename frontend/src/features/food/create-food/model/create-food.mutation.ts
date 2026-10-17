import { createFood } from '@src/entities/food/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateFoodMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createFood,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.foods.all,
      }),
  });
};
