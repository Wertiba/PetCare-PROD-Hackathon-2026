import { deleteEvent } from '@src/entities/event/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useDeleteEventMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteEvent,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.events.all,
      }),
  });
};
