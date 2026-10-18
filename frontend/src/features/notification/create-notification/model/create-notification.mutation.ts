import { createNotification } from '@src/entities/notification/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateNotificationMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createNotification,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.notifications.all,
      }),
  });
};
