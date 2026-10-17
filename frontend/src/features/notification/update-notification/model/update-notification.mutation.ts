import {
  UpdateNotificationReqDto,
  updateNotification,
} from '@src/entities/notification/api';
import { Uid } from '@src/shared/api/global.types';
import { useMutation } from '@tanstack/react-query';

export const useUpdateNotificationMutation = () =>
  useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateNotificationReqDto;
    }) => updateNotification(id, data),
  });
