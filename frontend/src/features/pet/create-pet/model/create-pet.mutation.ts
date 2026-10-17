import { createPet } from '@src/entities/pet/api';
import { useMutation } from '@tanstack/react-query';

export const useCreatePetMutation = () =>
  useMutation({
    mutationFn: createPet,
  });
