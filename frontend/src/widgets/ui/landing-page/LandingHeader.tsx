'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import Image from 'next/image';
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
          <span className="grid size-10 place-items-center bg-[var(--forest)] transition-transform group-hover:-rotate-6">
            <Image
              src="/images/petcare-mark.svg"
              alt=""
              width={40}
              height={40}
              className="size-full object-contain"
            />
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
            Возможности
          </a>
          <a
            href="#why"
            className="hidden text-sm tracking-[0.01em] text-[var(--cream)]/75 transition-colors hover:text-[var(--lime)] sm:inline"
          >
            Зачем это нужно
          </a>
          {isSessionRestored ? (
            user ? (
              <Link
                href="/dashboard"
                className="border-b border-[var(--lime)] pb-1 text-sm font-semibold tracking-[0.01em] text-[var(--cream)] transition-colors hover:text-[var(--lime)]"
              >
                Мои питомцы{' '}
                <span aria-hidden="true">↗</span>
              </Link>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  href="/register"
                  className="border-b border-[var(--lime)] pb-1 text-sm font-semibold tracking-[0.01em] text-[var(--cream)] transition-colors hover:text-[var(--lime)]"
                >
                  Создать аккаунт{' '}
                  <span aria-hidden="true">↗</span>
                </Link>
                <Link
                  href="/login"
                  className="border-b border-[var(--lime)] pb-1 text-sm font-semibold tracking-[0.01em] text-[var(--cream)] transition-colors hover:text-[var(--lime)]"
                >
                  Войти <span aria-hidden="true">↗</span>
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
