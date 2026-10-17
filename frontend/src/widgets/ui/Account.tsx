import Link from 'next/link';

import { AccountSettings } from './AccountSettings';
import { CareCalendar } from './CareCalendar';

type AccountTab = 'calendar' | 'settings';

interface AccountProps {
  activeTab: AccountTab;
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

const accountTabs = [
  {
    id: 'settings' as const,
    label: 'Настройки',
    icon: (
      <TabIcon>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.3 2.3-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-3.2v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-2.3-2.3.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H4.6v-3.2h.2a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L6 8l2.3-2.3.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h3.2v.2a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 8l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2V14H21a1.7 1.7 0 0 0-1.6 1Z" />
      </TabIcon>
    ),
  },
  {
    id: 'calendar' as const,
    label: 'Календарь',
    icon: (
      <TabIcon>
        <rect width="16" height="15" x="4" y="5" rx="2" />
        <path d="M8 3v4M16 3v4M4 10h16M8 14h.01M12 14h.01M16 14h.01" />
      </TabIcon>
    ),
  },
];

export function Account({ activeTab }: AccountProps) {
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
              Управляйте аккаунтом и планами ухода
            </p>
            <h1 className="mt-1 text-3xl font-black text-[var(--forest)] sm:text-4xl">
              Личный кабинет
            </h1>
          </div>
          <nav
            aria-label="Разделы личного кабинета"
            className="flex items-center rounded-md border border-[var(--forest)]/20 bg-white p-1"
          >
            {accountTabs.map((tab) => {
              const isActive = activeTab === tab.id;

              return (
                <Link
                  key={tab.id}
                  href={`/account?tab=${tab.id}`}
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
          {activeTab === 'settings' ? (
            <AccountSettings />
          ) : (
            <CareCalendar />
          )}
        </section>
      </main>
    </div>
  );
}
