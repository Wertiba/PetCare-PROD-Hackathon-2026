import { deleteState } from '@src/entities/state/api';
import { useMutation } from '@tanstack/react-query';

export const useDeleteStateMutation = () =>
  useMutation({
    mutationFn: deleteState,
  });
