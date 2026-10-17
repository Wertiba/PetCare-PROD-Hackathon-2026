'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { AdminAnimals } from './AdminAnimals';
import { AdminBreeds } from './AdminBreeds';
import { AdminCategories } from './AdminCategories';

type AdminTab = 'animals' | 'breeds' | 'categories';

interface AdminProps {
  activeTab: AdminTab;
}

interface TabIconProps {
  children: React.ReactNode;
}

function TabIcon({ children }: TabIconProps) {
  return (
    <svg
      aria-hidden="true"
      className="size-4"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
    >
      {children}
    </svg>
  );
}

const adminTabs = [
  {
    id: 'animals' as const,
    label: 'Виды',
    icon: (
      <TabIcon>
        <circle cx="5.5" cy="10" r="2" />
        <circle cx="9.5" cy="5.5" r="2" />
        <circle cx="14.5" cy="5.5" r="2" />
        <circle cx="18.5" cy="10" r="2" />
        <path d="M12 12c-3 0-6 3.5-6 6.2C6 20 7.3 21 9 21c1.2 0 2-.6 3-.6s1.8.6 3 .6c1.7 0 3-1 3-2.8C18 15.5 15 12 12 12Z" />
      </TabIcon>
    ),
  },
  {
    id: 'breeds' as const,
    label: 'Породы',
    icon: (
      <TabIcon>
        <path d="M4 6h16M4 12h16M4 18h10" />
      </TabIcon>
    ),
  },
  {
    id: 'categories' as const,
    label: 'Категории',
    icon: (
      <TabIcon>
        <rect width="7" height="7" x="3" y="3" rx="1" />
        <rect width="7" height="7" x="14" y="3" rx="1" />
        <rect width="7" height="7" x="3" y="14" rx="1" />
        <rect width="7" height="7" x="14" y="14" rx="1" />
      </TabIcon>
    ),
  },
];

export function Admin({ activeTab }: AdminProps) {
  const router = useRouter();
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );
  const isAdmin = user?.role === 'ADMIN';

  useEffect(() => {
    if (isSessionRestored && !isAdmin) {
      router.replace(user ? '/dashboard' : '/login');
    }
  }, [isSessionRestored, isAdmin, user, router]);

  return (
    <div className="min-h-dvh bg-[var(--cream)] text-[var(--ink)]">
      <header className="border-b border-[var(--forest)]/15 bg-[var(--cream)]">
        <div className="mx-auto flex min-h-18 w-full max-w-6xl items-center justify-between gap-4 px-5 py-3 sm:px-8 lg:px-10">
          <Link
            href="/dashboard"
            className="group flex items-center gap-3 text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--forest)]"
          >
            <span className="grid size-10 place-items-center rounded-sm bg-[var(--lime)] text-xl transition-transform group-hover:-rotate-6">
              +
            </span>
            <span className="text-lg font-black tracking-tight">
              PetCare
            </span>
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-sm border border-[var(--forest)]/30 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
          >
            <svg
              aria-hidden="true"
              className="size-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.8"
            >
              <path d="m15 18-6-6 6-6" />
            </svg>
            <span className="hidden sm:inline">
              К питомцам
            </span>
            <span className="sm:hidden">Назад</span>
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-5 py-7 sm:px-8 sm:py-10 lg:px-10">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[var(--forest)]/15 pb-5">
          <div>
            <p className="text-sm font-semibold text-[var(--ink)]/55">
              Справочники, общие для всех пользователей
            </p>
            <h1 className="mt-1 text-3xl font-black text-[var(--forest)] sm:text-4xl">
              Администрирование
            </h1>
          </div>
          <nav
            aria-label="Разделы администрирования"
            className="flex items-center rounded-md border border-[var(--forest)]/20 bg-white p-1"
          >
            {adminTabs.map((tab) => {
              const isActive = activeTab === tab.id;

              return (
                <Link
                  key={tab.id}
                  href={`/admin?tab=${tab.id}`}
                  aria-current={
                    isActive ? 'page' : undefined
                  }
                  className={`inline-flex items-center gap-2 rounded-sm px-3 py-2 text-sm font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] sm:px-4 ${
                    isActive
                      ? 'bg-[var(--lime)] text-[var(--forest)]'
                      : 'text-[var(--ink)]/65 hover:bg-[var(--cream)] hover:text-[var(--forest)]'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <section className="mt-7 rounded-md border border-[var(--forest)]/20 bg-white p-5 sm:p-7">
          {!isAdmin ? (
            <p
              role="status"
              className="text-sm text-[var(--ink)]/60"
            >
              Проверяем доступ…
            </p>
          ) : activeTab === 'animals' ? (
            <AdminAnimals />
          ) : activeTab === 'breeds' ? (
            <AdminBreeds />
          ) : (
            <AdminCategories />
          )}
        </section>
      </main>
    </div>
  );
}
