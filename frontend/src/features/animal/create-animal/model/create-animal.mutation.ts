import { createAnimal } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateAnimalMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createAnimal,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.animals.all,
      }),
  });
};
