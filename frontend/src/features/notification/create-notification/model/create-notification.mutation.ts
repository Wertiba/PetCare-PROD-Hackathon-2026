import { createNotification } from '@src/entities/notification/api';
import { useMutation } from '@tanstack/react-query';

export const useCreateNotificationMutation = () =>
  useMutation({
    mutationFn: createNotification,
  });
