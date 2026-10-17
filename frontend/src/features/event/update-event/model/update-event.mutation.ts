import {
  UpdateEventReqDto,
  updateEvent,
} from '@src/entities/event/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdateEventMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateEventReqDto;
    }) => updateEvent(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.events.all,
      }),
  });
};
