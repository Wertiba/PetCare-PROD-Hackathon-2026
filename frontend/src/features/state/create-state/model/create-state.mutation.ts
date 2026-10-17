import { createState } from '@src/entities/state/api';
import { useMutation } from '@tanstack/react-query';

export const useCreateStateMutation = () =>
  useMutation({
    mutationFn: createState,
  });
