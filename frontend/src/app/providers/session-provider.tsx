'use client';

import { useUserStore } from '@src/entities/user';
import { fetchUser } from '@src/entities/user/api/fetch-user';
import { setOnUnauthorized } from '@src/shared/api';
import { getAccessToken } from '@src/shared/lib';
import { useEffect } from 'react';

/**
 * Restores the session from the persisted access token on load and keeps the
 * user store in sync when the session becomes unrecoverable.
 */
export function SessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const setUser = useUserStore((state) => state.setUser);
  const clearUser = useUserStore(
    (state) => state.clearUser,
  );

  useEffect(() => {
    setOnUnauthorized(clearUser);

    if (!getAccessToken()) return;

    fetchUser()
      .then(setUser)
      .catch(() => {
        // 401 is already handled by the API client (refresh + cleanup);
        // any other failure just means no session to restore.
      });
  }, [setUser, clearUser]);

  return <>{children}</>;
}
