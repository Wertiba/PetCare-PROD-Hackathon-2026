import { createPet } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreatePetMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createPet,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};
