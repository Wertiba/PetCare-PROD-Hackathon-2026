'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import Link from 'next/link';

export default function LandingHeader() {
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );

  return (
    <header className="border-b border-[var(--ink)] bg-[var(--forest)] text-[var(--cream)]">
      <div className="mx-auto flex min-h-16 w-full max-w-[1440px] items-center justify-between px-5 py-3 sm:px-8 lg:px-12">
        <Link
          href="/"
          className="group flex items-center gap-3"
          aria-label="главная petcare"
        >
          <span className="grid size-8 place-items-center border border-[var(--cream)] bg-[var(--lime)] text-sm font-black text-[var(--forest)] transition-transform group-hover:-rotate-6">
            +
          </span>
          <span className="font-mono text-xs font-bold uppercase tracking-[0.22em]">
            petcare
          </span>
        </Link>
        <nav
          aria-label="Основная навигация"
          className="flex items-center gap-5 sm:gap-8"
        >
          <a
            href="#inside"
            className="hidden text-sm tracking-[0.01em] text-[var(--cream)]/75 transition-colors hover:text-[var(--lime)] sm:inline"
          >
            возможности
          </a>
          <a
            href="#why"
            className="hidden text-sm tracking-[0.01em] text-[var(--cream)]/75 transition-colors hover:text-[var(--lime)] sm:inline"
          >
            зачем это нужно
          </a>
          {isSessionRestored ? (
            user ? (
              <Link
                href="/dashboard"
                className="border-b border-[var(--lime)] pb-1 text-sm font-semibold tracking-[0.01em] text-[var(--cream)] transition-colors hover:text-[var(--lime)]"
              >
                мои питомцы{' '}
                <span aria-hidden="true">↗</span>
              </Link>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  href="/register"
                  className="hidden text-sm font-semibold tracking-[0.01em] text-[var(--cream)]/80 transition-colors hover:text-[var(--lime)] sm:inline"
                >
                  создать аккаунт
                </Link>
                <Link
                  href="/login"
                  className="border-b border-[var(--lime)] pb-1 text-sm font-semibold tracking-[0.01em] text-[var(--cream)] transition-colors hover:text-[var(--lime)]"
                >
                  войти <span aria-hidden="true">↗</span>
                </Link>
              </div>
            )
          ) : (
            <span
              aria-hidden="true"
              className="h-5 w-20 animate-pulse bg-[var(--cream)]/15"
            />
          )}
        </nav>
      </div>
    </header>
  );
}
