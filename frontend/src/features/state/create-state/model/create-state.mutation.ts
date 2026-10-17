import { createState } from '@src/entities/state/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateStateMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createState,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.states.all,
      }),
  });
};
