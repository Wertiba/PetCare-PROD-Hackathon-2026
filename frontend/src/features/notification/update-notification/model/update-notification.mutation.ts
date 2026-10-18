import {
  UpdateNotificationReqDto,
  updateNotification,
} from '@src/entities/notification/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdateNotificationMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateNotificationReqDto;
    }) => updateNotification(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.notifications.all,
      }),
  });
};
