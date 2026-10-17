'use client';

import {
  updateUser,
  useUserStore,
} from '@src/entities/user';
import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

export function useUpdateFullNameMutation() {
  const queryClient = useQueryClient();
  const setUser = useUserStore((state) => state.setUser);

  return useMutation({
    mutationFn: updateUser,
    onSuccess: (user) => {
      setUser(user);
      queryClient.setQueryData(queryKeys.user.me, user);
    },
  });
}
