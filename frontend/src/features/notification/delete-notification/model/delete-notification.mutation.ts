import { deleteNotification } from '@src/entities/notification/api';
import { useMutation } from '@tanstack/react-query';

export const useDeleteNotificationMutation = () =>
  useMutation({
    mutationFn: deleteNotification,
  });
