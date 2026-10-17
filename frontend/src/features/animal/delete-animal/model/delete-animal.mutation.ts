import { deleteAnimal } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useDeleteAnimalMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteAnimal,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.animals.all,
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.breeds.all,
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.pets.all,
        }),
      ]),
  });
};
