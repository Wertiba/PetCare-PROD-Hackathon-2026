import { deleteEvent } from '@src/entities/event/api';
import { useMutation } from '@tanstack/react-query';

export const useDeleteEventMutation = () =>
  useMutation({
    mutationFn: deleteEvent,
  });
