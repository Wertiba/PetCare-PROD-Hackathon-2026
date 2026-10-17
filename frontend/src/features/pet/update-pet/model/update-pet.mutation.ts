import {
  UpdatePetReqDto,
  updatePet,
} from '@src/entities/pet/api';
import { Uid } from '@src/shared/api/global.types';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUpdatePetMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdatePetReqDto;
    }) => updatePet(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};
