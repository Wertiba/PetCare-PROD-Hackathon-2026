'use client';

import { useUserStore } from '@src/entities/user';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { login } from '../api/login';

export function useLoginMutation() {
  const router = useRouter();
  const setUser = useUserStore((state) => state.setUser);
  const setSessionRestored = useUserStore(
    (state) => state.setSessionRestored,
  );

  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setUser(data.user);
      setSessionRestored();
      router.replace(
        data.user.role === 'ADMIN'
          ? '/admin'
          : '/dashboard',
      );
    },
  });
}
