import {
  UpdateBreedReqDto,
  updateBreed,
} from '@src/entities/pet/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdateBreedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateBreedReqDto;
    }) => updateBreed(id, data),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.breeds.all,
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.pets.all,
        }),
      ]),
  });
};
