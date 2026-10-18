'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { Dashboard } from '@src/widgets';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const router = useRouter();
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );

  useEffect(() => {
    if (isSessionRestored && !user) {
      router.replace('/');
    }
  }, [isSessionRestored, router, user]);

  if (!isSessionRestored || !user) {
    return null;
  }

  return <Dashboard />;
}
