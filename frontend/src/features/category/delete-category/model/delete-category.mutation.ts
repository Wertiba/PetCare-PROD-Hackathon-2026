import { deleteCategory } from '@src/entities/category/api';
import { useMutation } from '@tanstack/react-query';

export const useDeleteCategoryMutation = () =>
  useMutation({
    mutationFn: deleteCategory,
  });
