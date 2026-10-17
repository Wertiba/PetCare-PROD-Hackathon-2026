import {
  UpdateCategoryReqDto,
  updateCategory,
} from '@src/entities/category/api';
import { Uid } from '@src/shared/api/global.types';
import { useMutation } from '@tanstack/react-query';

export const useUpdateCategoryMutation = () =>
  useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: Uid;
      data: UpdateCategoryReqDto;
    }) => updateCategory(id, data),
  });
