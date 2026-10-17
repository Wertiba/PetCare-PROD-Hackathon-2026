import { createNote } from '@src/entities/note';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useCreateNoteMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createNote,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.notes.all,
      }),
  });
};
