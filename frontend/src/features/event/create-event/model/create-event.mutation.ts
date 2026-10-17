import { createEvent } from '@src/entities/event/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateEventMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createEvent,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.events.all,
      }),
  });
};
