import {
  UpdatePetReqDto,
  updatePet,
} from '@src/entities/pet/api';
import { Uid } from '@src/shared/api/global.types';
import { useMutation } from '@tanstack/react-query';

export const useUpdatePetMutation = () =>
  useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdatePetReqDto;
    }) => updatePet(id, data),
  });
