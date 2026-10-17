'use client';

import { UpdateFullNameForm } from '@src/features/user/update-full-name';
import {
  type Theme,
  applyTheme,
  getStoredTheme,
  subscribeToTheme,
} from '@src/shared/lib/theme';
import { useSyncExternalStore } from 'react';

function ThemeIcon({ dark }: { dark: boolean }) {
  return (
    <svg
      aria-hidden="true"
      className="size-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
    >
      {dark ? (
        <path d="M20.2 15.1A8.5 8.5 0 0 1 8.9 3.8 8.5 8.5 0 1 0 20.2 15Z" />
      ) : (
        <>
          <circle cx="12" cy="12" r="3.5" />
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </>
      )}
    </svg>
  );
}

export function AccountSettings() {
  const theme = useSyncExternalStore(
    subscribeToTheme,
    getStoredTheme,
    () => 'light',
  );
  const isDarkThemeSelected = theme === 'dark';

  const selectTheme = (nextTheme: Theme) => {
    applyTheme(nextTheme);
  };

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.72fr)]">
      <section aria-labelledby="account-name-heading">
        <div className="flex items-center gap-3">
          <span className="grid size-10 place-items-center rounded-sm bg-[var(--lime)] text-[var(--forest)]">
            <svg
              aria-hidden="true"
              className="size-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.8"
            >
              <circle cx="12" cy="8" r="3.5" />
              <path d="M5 21a7 7 0 0 1 14 0" />
            </svg>
          </span>
          <div>
            <p className="text-sm font-semibold text-[var(--ink)]/55">
              Профиль
            </p>
            <h2
              id="account-name-heading"
              className="text-xl font-black text-[var(--forest)]"
            >
              Как вас называть
            </h2>
          </div>
        </div>
        <p className="mt-4 max-w-lg text-sm leading-6 text-[var(--ink)]/65">
          Это имя увидите вы в личном кабинете.
        </p>
        <UpdateFullNameForm />
      </section>

      <section
        aria-labelledby="theme-heading"
        className="border-t border-[var(--forest)]/15 pt-7 lg:border-t-0 lg:border-l lg:pl-8 lg:pt-0"
      >
        <div className="flex items-center gap-3">
          <span className="grid size-10 place-items-center rounded-sm bg-[var(--forest)] text-[var(--cream)]">
            <ThemeIcon dark={isDarkThemeSelected} />
          </span>
          <div>
            <p className="text-sm font-semibold text-[var(--ink)]/55">
              Оформление
            </p>
            <h2
              id="theme-heading"
              className="text-xl font-black text-[var(--forest)]"
            >
              Тема сайта
            </h2>
          </div>
        </div>
        <p className="mt-4 text-sm leading-6 text-[var(--ink)]/65">
          Выберите комфортный вид интерфейса. Настройка
          сохранится для следующих посещений.
        </p>
        <div className="mt-5 inline-flex rounded-md border border-[var(--forest)]/20 bg-[var(--cream)] p-1">
          <button
            type="button"
            aria-pressed={!isDarkThemeSelected}
            onClick={() => selectTheme('light')}
            className={`inline-flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] ${
              !isDarkThemeSelected
                ? 'bg-white text-[var(--forest)]'
                : 'text-[var(--ink)]/55 hover:text-[var(--forest)]'
            }`}
          >
            <ThemeIcon dark={false} />
            Светлая
          </button>
          <button
            type="button"
            aria-pressed={isDarkThemeSelected}
            onClick={() => selectTheme('dark')}
            className={`inline-flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] ${
              isDarkThemeSelected
                ? 'bg-[var(--forest)] text-[var(--cream)]'
                : 'text-[var(--ink)]/55 hover:text-[var(--forest)]'
            }`}
          >
            <ThemeIcon dark />
            Тёмная
          </button>
        </div>
      </section>
    </div>
  );
}
