'use client';

import { useUserStore } from '@src/entities/user';
import { queryKeys } from '@src/shared/api/query-keys';
import { clearAccessToken } from '@src/shared/lib';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { logout } from '../api/logout';

export function useLogoutMutation() {
  const qc = useQueryClient();
  const clearUser = useUserStore(
    (state) => state.clearUser,
  );

  return useMutation({
    mutationFn: logout,
    onSettled: () => {
      clearAccessToken();
      clearUser();
      qc.removeQueries({ queryKey: queryKeys.user.me });
    },
  });
}
