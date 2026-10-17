import {
  UpdateAnimalReqDto,
  updateAnimal,
} from '@src/entities/pet/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdateAnimalMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateAnimalReqDto;
    }) => updateAnimal(id, data),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.animals.all,
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.pets.all,
        }),
      ]),
  });
};
