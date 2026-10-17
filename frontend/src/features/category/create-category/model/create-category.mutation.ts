import { createCategory } from '@src/entities/category/api';
import { useMutation } from '@tanstack/react-query';

export const useCreateCategoryMutation = () =>
  useMutation({
    mutationFn: createCategory,
  });
