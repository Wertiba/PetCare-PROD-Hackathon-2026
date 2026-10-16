'use client';

import { useUserStore } from '@src/entities/user';
import { setAccessToken } from '@src/shared/lib';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { login } from '../api/login';

export function useLoginMutation() {
  const router = useRouter();
  const setUser = useUserStore((state) => state.setUser);

  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setAccessToken(data.accessToken);
      setUser(data.user);
      router.push('/');
    },
  });
}
