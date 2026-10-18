import {
  generatePetAvatar,
  selectPetAvatar,
  uploadPetPhoto,
} from '@src/entities/pet/api';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export const useUploadPetPhotoMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      petId,
      file,
    }: {
      petId: string;
      file: File;
    }) => uploadPetPhoto(petId, file),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};

export const useGeneratePetAvatarMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: generatePetAvatar,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};

export const useSelectPetAvatarMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      petId,
      source,
    }: {
      petId: string;
      source: 'photo' | 'generated';
    }) => selectPetAvatar(petId, source),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: queryKeys.pets.all,
      }),
  });
};
