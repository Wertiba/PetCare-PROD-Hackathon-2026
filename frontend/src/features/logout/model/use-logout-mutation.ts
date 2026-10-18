'use client';

import { useUserStore } from '@src/entities/user';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { logout } from '../api/logout';

export function useLogoutMutation() {
  const qc = useQueryClient();
  const router = useRouter();
  const clearUser = useUserStore(
    (state) => state.clearUser,
  );

  return useMutation({
    mutationFn: logout,
    onSettled: () => {
      clearUser();
      qc.clear();
      router.replace('/');
    },
  });
}
