'use client';

import type { ComponentProps, ReactNode } from 'react';

export type DashboardTool =
  'health' | 'food' | 'reminders' | 'widget';

interface DashboardSidebarProps {
  activeTool: DashboardTool | 'home';
  hasPet: boolean;
  onToolChange: (tool: DashboardTool | 'home') => void;
}

interface ToolItem {
  icon: ReactNode;
  id: DashboardTool;
  label: string;
}

function ToolIcon({
  children,
  ...props
}: ComponentProps<'svg'>) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      {...props}
    >
      {children}
    </svg>
  );
}

const tools: ToolItem[] = [
  {
    id: 'health',
    label: 'Здоровье',
    icon: (
      <ToolIcon>
        <path d="M20.8 4.7a5.5 5.5 0 0 0-7.8 0L12 5.8l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.9-8.5a5.5 5.5 0 0 0-.1-7.8Z" />
      </ToolIcon>
    ),
  },
  {
    id: 'food',
    label: 'Питание',
    icon: (
      <ToolIcon>
        <path d="M4 3v7M7 3v7M4 6.5h3M5.5 10v11M16 3v18M16 3c2.5 0 4 1.8 4 4s-1.5 4-4 4" />
      </ToolIcon>
    ),
  },
  {
    id: 'reminders',
    label: 'Напоминания',
    icon: (
      <ToolIcon>
        <rect width="16" height="15" x="4" y="5" rx="2" />
        <path d="M8 3v4M16 3v4M4 10h16M8 14h.01M12 14h.01M16 14h.01" />
      </ToolIcon>
    ),
  },
  {
    id: 'widget',
    label: 'Виджет питомца',
    icon: (
      <ToolIcon>
        <rect width="6" height="6" x="4" y="4" rx="1" />
        <rect width="6" height="6" x="14" y="4" rx="1" />
        <rect width="6" height="6" x="4" y="14" rx="1" />
        <rect width="6" height="6" x="14" y="14" rx="1" />
      </ToolIcon>
    ),
  },
];

export function DashboardSidebar({
  activeTool,
  hasPet,
  onToolChange,
}: DashboardSidebarProps) {
  return (
    <aside className="border-b border-[var(--forest)]/20 bg-white lg:border-r lg:border-b-0">
      <div className="flex h-full flex-col px-3 py-5 sm:px-5 lg:px-4">
        <nav aria-label="Главная" className="mb-4">
          <button
            aria-current={
              activeTool === 'home' ? 'page' : undefined
            }
            type="button"
            onClick={() => onToolChange('home')}
            className={`group flex w-full shrink-0 items-center gap-3 rounded-sm px-3 py-2.5 text-left text-sm font-bold transition-colors focus-visible:ring-2 focus-visible:ring-[var(--forest)] focus-visible:ring-offset-2 ${
              activeTool === 'home'
                ? 'bg-[var(--lime)] text-[var(--forest)]'
                : 'text-[var(--ink)]/70 hover:bg-[var(--cream)] hover:text-[var(--forest)]'
            }`}
          >
            <span className="grid size-7 shrink-0 place-items-center rounded-sm border border-current/15 bg-white/50 p-1.5 transition-colors group-hover:bg-white">
              <ToolIcon>
                <path d="m3 11 9-8 9 8M5 10v10h14V10M9 20v-6h6v6" />
              </ToolIcon>
            </span>
            <span className="whitespace-nowrap">
              Главная
            </span>
          </button>
        </nav>

        <div className="mb-4 hidden border-t border-[var(--forest)]/20 px-2 pt-4 lg:block">
          <p className="text-[10px] font-black tracking-[.16em] text-[var(--forest)]/45 uppercase">
            Забота
          </p>
          <p className="mt-1 text-xs text-[var(--ink)]/50">
            Инструменты питомца
          </p>
        </div>

        <nav
          aria-label="Инструменты питомца"
          className="flex gap-1 overflow-x-auto pb-1 lg:block lg:overflow-visible"
        >
          {tools.map((item) => {
            const active = activeTool === item.id;

            return (
              <button
                aria-current={active ? 'page' : undefined}
                disabled={!hasPet}
                key={item.id}
                onClick={() => onToolChange(item.id)}
                type="button"
                className={`group flex shrink-0 items-center gap-3 rounded-sm px-3 py-2.5 text-left text-sm font-semibold transition-colors focus-visible:ring-2 focus-visible:ring-[var(--forest)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-45 lg:mb-1 lg:w-full ${
                  active && hasPet
                    ? 'bg-[var(--lime)] text-[var(--forest)]'
                    : 'text-[var(--ink)]/70 hover:bg-[var(--cream)] hover:text-[var(--forest)]'
                }`}
              >
                <span className="grid size-7 shrink-0 place-items-center rounded-sm border border-current/15 bg-white/50 p-1.5 transition-colors group-hover:bg-white">
                  {item.icon}
                </span>
                <span className="whitespace-nowrap">
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>

        {!hasPet ? (
          <div className="mt-4 hidden rounded-sm border border-dashed border-[var(--forest)]/25 bg-[var(--cream)] px-3 py-3 lg:block">
            <div className="flex items-start gap-2.5">
              <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-sm bg-[var(--lime)] text-[var(--forest)]">
                <ToolIcon className="size-3.5">
                  <path d="M12 7v5M12 16h.01" />
                  <path d="M10.3 3.7 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z" />
                </ToolIcon>
              </span>
              <p className="text-xs leading-5 text-[var(--ink)]/60">
                Добавьте питомца — тогда здесь появятся его
                данные и инструменты ухода.
              </p>
            </div>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
