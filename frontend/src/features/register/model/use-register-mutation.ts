'use client';

import { useUserStore } from '@src/entities/user';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { register } from '../api/register';
import type { RegisterDto } from '../api/register.dto';

export function useRegisterMutation() {
  const router = useRouter();
  const setUser = useUserStore((state) => state.setUser);
  const setSessionRestored = useUserStore(
    (state) => state.setSessionRestored,
  );

  return useMutation({
    mutationFn: (data: RegisterDto) => register(data),
    onSuccess: (result) => {
      setUser(result.user);
      setSessionRestored();
      router.replace('/dashboard');
    },
  });
}
