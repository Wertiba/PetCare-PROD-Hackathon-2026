'use client';

import {
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { useLogoutMutation } from '@src/features/logout';

import { whiteLinkClasses } from './Header';

export function UserMenu() {
  const user = useUserStore(selectUser);
  const { mutate: logout, isPending } = useLogoutMutation();

  if (!user) return null;

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="ml-auto flex items-center gap-3 text-sm whitespace-nowrap">
      <span className="hidden text-neutral-600 sm:inline">
        {user.name}
      </span>
      <button
        type="button"
        onClick={handleLogout}
        disabled={isPending}
        className={whiteLinkClasses}
      >
        {isPending ? 'выходим…' : 'выйти'}
      </button>
    </div>
  );
}
