'use client';

import {
  fetchUser,
  useUserStore,
} from '@src/entities/user';
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
  const setSessionRestored = useUserStore(
    (state) => state.setSessionRestored,
  );

  useEffect(() => {
    setOnUnauthorized(clearUser);

    if (!getAccessToken()) {
      setSessionRestored();
      return;
    }

    fetchUser()
      .then(setUser)
      .catch(() => {
        // 401 is already handled by the API client (refresh + cleanup);
        // any other failure just means no session to restore.
      })
      .finally(setSessionRestored);
  }, [setUser, clearUser, setSessionRestored]);

  return <>{children}</>;
}
