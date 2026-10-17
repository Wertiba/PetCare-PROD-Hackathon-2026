import { deletePet } from '@src/entities/pet/api';
import { useMutation } from '@tanstack/react-query';

export const useDeletePetMutation = () =>
  useMutation({
    mutationFn: deletePet,
  });
