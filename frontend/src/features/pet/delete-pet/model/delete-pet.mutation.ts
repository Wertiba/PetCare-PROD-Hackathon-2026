import { deletePet } from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useDeletePetMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deletePet,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};
