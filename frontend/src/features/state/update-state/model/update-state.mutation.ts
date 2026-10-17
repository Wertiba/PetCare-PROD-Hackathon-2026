import {
  UpdateStateReqDto,
  updateState,
} from '@src/entities/state/api';
import { Uid } from '@src/shared/api/global.types';
import { useMutation } from '@tanstack/react-query';

export const useUpdateStateMutation = () =>
  useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateStateReqDto;
    }) => updateState(id, data),
  });
