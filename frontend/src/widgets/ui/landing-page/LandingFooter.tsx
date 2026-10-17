'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import Link from 'next/link';

export default function LandingFooter() {
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );

  return (
    <footer className="border-t border-[var(--ink)] bg-[var(--cream)] px-5 py-5 sm:px-8 lg:px-12">
      <div className="mx-auto flex w-full max-w-[1440px] flex-col gap-5 font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[var(--forest)]/65 sm:flex-row sm:items-center sm:justify-between">
        <span>petcare / для каждого дня</span>
        {isSessionRestored ? (
          user ? (
            <Link
              href="/dashboard"
              className="transition-colors hover:text-[var(--forest)]"
            >
              мои питомцы
            </Link>
          ) : (
            <div className="flex gap-6">
              <Link
                href="/login"
                className="transition-colors hover:text-[var(--forest)]"
              >
                войти
              </Link>
              <Link
                href="/register"
                className="transition-colors hover:text-[var(--forest)]"
              >
                регистрация
              </Link>
            </div>
          )
        ) : (
          <span
            aria-hidden="true"
            className="h-3 w-24 animate-pulse bg-[var(--forest)]/10"
          />
        )}
      </div>
    </footer>
  );
}
