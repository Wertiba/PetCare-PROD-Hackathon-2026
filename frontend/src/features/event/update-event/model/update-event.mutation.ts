import {
  UpdateEventReqDto,
  updateEvent,
} from '@src/entities/event/api';
import { Uid } from '@src/shared/api/global.types';
import { useMutation } from '@tanstack/react-query';

export const useUpdateEventMutation = () =>
  useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateEventReqDto;
    }) => updateEvent(id, data),
  });
