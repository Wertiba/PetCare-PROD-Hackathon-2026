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
    // The pet's events and reminders go with it, including in the all-pets upcoming list.
    onSuccess: () =>
      Promise.all(
        [
          queryKeys.pets.all,
          queryKeys.events.all,
          queryKeys.notifications.all,
        ].map((queryKey) =>
          queryClient.invalidateQueries({ queryKey }),
        ),
      ),
  });
};
