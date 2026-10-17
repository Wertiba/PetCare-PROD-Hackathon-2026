import { createEvent } from '@src/entities/event/api';
import { useMutation } from '@tanstack/react-query';

export const useCreateEventMutation = () =>
  useMutation({
    mutationFn: createEvent,
  });
