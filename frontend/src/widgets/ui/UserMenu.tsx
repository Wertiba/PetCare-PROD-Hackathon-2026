'use client';

import {
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { useLogoutMutation } from '@src/features/logout';
import { clearAccessToken } from '@src/shared/lib';

import { whiteLinkClasses } from './Header';

export function UserMenu() {
  const user = useUserStore(selectUser);
  const clearUser = useUserStore(
    (state) => state.clearUser,
  );
  const { mutate: logout, isPending } = useLogoutMutation();

  if (!user) return null;

  const handleLogout = () => {
    logout(undefined, {
      onSettled: () => {
        // Clear the local session even if the backend call failed (e.g. the
        // refresh cookie is already gone and the endpoint returns 401).
        clearAccessToken();
        clearUser();
      },
    });
  };

  return (
    <div className="ml-auto flex items-center gap-3 text-sm whitespace-nowrap">
      <span className="hidden text-neutral-600 sm:inline">
        {user.email}
      </span>
      <button
        type="button"
        onClick={handleLogout}
        disabled={isPending}
        className={whiteLinkClasses}
      >
        {isPending ? 'logging out…' : 'log out'}
      </button>
    </div>
  );
}
