import { createBreed } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateBreedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createBreed,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.breeds.all,
      }),
  });
};
