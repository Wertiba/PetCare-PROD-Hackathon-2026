'use client';

import { queryKeys } from '@src/shared/api/query-keys';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { logout } from '../api/logout';

export function useLogoutMutation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: logout,
    onSuccess: () =>
      qc.removeQueries({ queryKey: queryKeys.user.me }),
  });
}
