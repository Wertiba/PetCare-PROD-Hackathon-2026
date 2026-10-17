import { deleteBreed } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useDeleteBreedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteBreed,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.breeds.all,
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.pets.all,
        }),
      ]),
  });
};
