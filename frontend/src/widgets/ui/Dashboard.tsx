'use client';

import {
  type Event,
  useGetEventsQuery,
  useGetUpcomingEventsQuery,
} from '@src/entities/event';
import { useGetNotificationsQuery } from '@src/entities/notification';
import {
  type Pet,
  useGetPetQuery,
} from '@src/entities/pet';
import { useGetStatesQuery } from '@src/entities/state';
import {
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { useLogoutMutation } from '@src/features/logout';
import { CreatePetForm } from '@src/features/pet/create-pet';
import { useDeletePetMutation } from '@src/features/pet/delete-pet';
import { EditPetForm } from '@src/features/pet/update-pet';
import { createPetColorMap } from '@src/shared/lib';
import { Dialog } from '@src/shared/ui';
import { CareCalendar } from '@src/widgets/ui/CareCalendar';
import {
  DashboardSidebar,
  type DashboardTool,
} from '@src/widgets/ui/DashboardSidebar';
import { FoodPanel } from '@src/widgets/ui/FoodPanel';
import { HealthPanel } from '@src/widgets/ui/HealthPanel';
import { PetHome } from '@src/widgets/ui/PetHome';
import { ReminderToast } from '@src/widgets/ui/ReminderToast';
import { motion, useReducedMotion } from 'motion/react';
import Image from 'next/image';
import Link from 'next/link';
import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

type Tool = 'home' | DashboardTool;
const formatDate = (value: number | null | undefined) =>
  value
    ? new Intl.DateTimeFormat('ru-RU', {
        dateStyle: 'medium',
      }).format(new Date(value * 1000))
    : 'Не указано';

function ChevronDown() {
  return (
    <span
      aria-hidden="true"
      className="grid size-5 place-items-center"
    >
      <svg
        className="size-4"
        fill="none"
        viewBox="0 0 16 16"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2.25"
      >
        <path d="m4 6 4 4 4-4" />
      </svg>
    </span>
  );
}

function PetModal({
  children,
  close,
  title,
}: {
  children: React.ReactNode;
  close: () => void;
  title: string;
}) {
  return (
    <Dialog labelledBy="pet-modal-title" onClose={close}>
      <div className="mx-auto w-2xl max-w-full p-5 sm:p-6">
        <div className="mb-5 flex justify-between border-b border-[var(--forest)]/15 pb-4">
          <div>
            <p className="text-xs font-bold tracking-[.12em] text-[var(--forest)]/60 uppercase">
              Профиль питомца
            </p>
            <h2
              id="pet-modal-title"
              className="mt-1 text-2xl font-black text-[var(--forest)]"
            >
              {title}
            </h2>
          </div>
          <button
            onClick={close}
            type="button"
            aria-label="Закрыть"
            className="size-9 rounded-sm border border-[var(--forest)]"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </Dialog>
  );
}
function Panel({ pet, tool }: { pet: Pet; tool: Tool }) {
  const events = useGetEventsQuery({
    page: 0,
    size: 12,
    petId: pet.id,
  });
  const reminders = useGetNotificationsQuery({
    page: 0,
    size: 20,
    petId: pet.id,
    due: true,
  });
  const states = useGetStatesQuery({
    page: 0,
    size: 8,
    petId: pet.id,
  });
  if (tool === 'widget')
    return (
      <section className="grid gap-5 md:grid-cols-2">
        <div className="rounded-md border-2 border-[var(--forest)] bg-[var(--forest)] p-6 text-white shadow-[5px_5px_0_var(--lime)]">
          <p className="text-xs font-bold tracking-[.12em] text-[var(--lime)] uppercase">
            Дополнительно
          </p>
          <h2 className="mt-3 text-3xl font-black">
            Виджет {pet.name}
          </h2>
          <p className="mt-4 text-white/70">
            Важные процедуры и события рядом на рабочем
            столе.
          </p>
        </div>
        <div className="rounded-md border border-[var(--forest)]/25 bg-white p-6">
          <h3 className="font-black text-[var(--forest)]">
            Подключение виджета
          </h3>
          <p className="mt-3 text-sm leading-6 text-[var(--ink)]/65">
            Виджет использует существующие напоминания
            питомца после настройки на стороне приложения.
          </p>
        </div>
      </section>
    );
  const list =
    tool === 'reminders'
      ? reminders.data?.items.map((item) => (
          <div
            key={item.id}
            className="border-b border-[var(--forest)]/10 pb-3"
          >
            <b>{item.eventName}</b>
            <p className="text-sm text-[var(--ink)]/60">
              {formatDate(item.time)}
            </p>
          </div>
        ))
      : events.data?.items.map((item) => (
          <div
            key={item.id}
            className="border-b border-[var(--forest)]/10 pb-3"
          >
            <b>{item.name}</b>
            <p className="text-sm text-[var(--ink)]/60">
              {formatDate(item.schedule)} · {item.status}
            </p>
          </div>
        ));
  const title =
    tool === 'reminders'
      ? 'Ближайшие напоминания'
      : 'История здоровья';
  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
      <section className="rounded-md border-2 border-[var(--forest)] bg-white p-5 shadow-[4px_4px_0_var(--lime)]">
        <h2 className="text-xl font-black text-[var(--forest)]">
          {title}
        </h2>
        <div className="mt-5 space-y-3">
          {list?.length ? (
            list
          ) : (
            <p className="py-6 text-sm text-[var(--ink)]/60">
              Пока нет записей.
            </p>
          )}
        </div>
      </section>
      {tool === 'health' ? (
        <section className="rounded-md border border-[var(--forest)]/25 bg-white p-5">
          <h2 className="text-xl font-black text-[var(--forest)]">
            Метрики
          </h2>
          <div className="mt-5 space-y-3">
            {states.data?.items.map((item) => (
              <div
                key={item.id}
                className="flex justify-between border-b border-[var(--forest)]/10 pb-2"
              >
                <span>Показатель</span>
                <b>{item.value}</b>
              </div>
            )) ?? (
              <p className="text-sm text-[var(--ink)]/60">
                Нет измерений.
              </p>
            )}
          </div>
        </section>
      ) : (
        <section className="rounded-md border border-[var(--forest)]/25 bg-[var(--cream)] p-5">
          <h2 className="text-xl font-black text-[var(--forest)]">
            {pet.name}
          </h2>
          <p className="mt-3 text-sm leading-6 text-[var(--ink)]/65">
            Напоминания строятся из запланированных
            процедур.
          </p>
        </section>
      )}
    </div>
  );
}

export function Dashboard() {
  const user = useUserStore(selectUser);
  const petsQuery = useGetPetQuery({ page: 0, size: 100 });
  const logout = useLogoutMutation();
  const deletion = useDeletePetMutation();
  const [tool, setTool] = useState<Tool>('home');
  const [reminderEvent, setReminderEvent] = useState<
    Event | undefined
  >();
  const [selectedId, setSelectedId] = useState<
    string | null
  >(null);
  const [dialog, setDialog] = useState<
    'create' | 'edit' | 'delete' | null
  >(null);
  const [notificationsOpen, setNotificationsOpen] =
    useState(false);
  const [petsOpen, setPetsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const petsMenuRef = useRef<HTMLDivElement>(null);
  const notificationsMenuRef = useRef<HTMLDivElement>(null);
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const upcomingEvents = useGetUpcomingEventsQuery({
    days: 30,
    page: 0,
    size: 100,
  });
  const petItems = petsQuery.data?.items;
  const pets = useMemo(() => petItems ?? [], [petItems]);
  const petColorById = useMemo(
    () => createPetColorMap(pets.map((item) => item.id)),
    [pets],
  );
  const petNameById = useMemo(
    () => new Map(pets.map((item) => [item.id, item.name])),
    [pets],
  );
  const pet =
    pets.find((item) => item.id === selectedId) ?? pets[0];
  const choose = (item: Pet) => {
    setSelectedId(item.id);
    setPetsOpen(false);
  };

  useEffect(() => {
    const closeMenus = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!petsMenuRef.current?.contains(target)) {
        setPetsOpen(false);
      }
      if (!notificationsMenuRef.current?.contains(target)) {
        setNotificationsOpen(false);
      }
      if (!profileMenuRef.current?.contains(target)) {
        setProfileOpen(false);
      }
    };

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setPetsOpen(false);
        setNotificationsOpen(false);
        setProfileOpen(false);
      }
    };

    document.addEventListener('pointerdown', closeMenus);
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener(
        'pointerdown',
        closeMenus,
      );
      document.removeEventListener(
        'keydown',
        closeOnEscape,
      );
    };
  }, []);
  return (
    <div className="min-h-dvh bg-[var(--cream)] text-[var(--ink)] lg:grid lg:grid-cols-[16rem_1fr] lg:grid-rows-[auto_1fr]">
      <header className="grid min-h-18 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-[var(--forest)]/15 px-5 py-3 sm:px-8 lg:col-span-2 lg:px-10">
        <div className="group flex items-center gap-3 text-[var(--forest)]">
          <span className="grid size-12 place-items-center rounded-2xl bg-[var(--forest)] transition-transform group-hover:-rotate-6">
            <Image
              src="/images/petcare-mark.svg"
              alt=""
              width={48}
              height={48}
              className="size-full object-contain"
            />
          </span>
          <span className="hidden text-lg font-black tracking-tight sm:inline">
            PetCare
          </span>
        </div>
        <div
          ref={petsMenuRef}
          className="relative flex min-w-0 justify-center"
        >
          {pet ? (
            <>
              <button
                type="button"
                onClick={() => {
                  setPetsOpen((value) => !value);
                  setNotificationsOpen(false);
                  setProfileOpen(false);
                }}
                aria-expanded={petsOpen}
                aria-haspopup="listbox"
                aria-label="Выбрать питомца"
                className="grid min-w-0 max-w-64 grid-cols-[auto_minmax(0,1fr)_1.25rem] items-center gap-2 rounded-md border border-[var(--forest)]/55 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] transition-colors hover:bg-[var(--cream)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
              >
                <span className="hidden leading-none text-xs font-bold tracking-[.08em] text-[var(--forest)]/50 uppercase sm:inline">
                  Питомец
                </span>
                <span className="min-w-0 truncate leading-none">
                  {pet.name}
                </span>
                <ChevronDown />
              </button>
              {petsOpen ? (
                <div
                  role="listbox"
                  aria-label="Питомцы"
                  className="absolute top-[calc(100%+.65rem)] left-1/2 z-40 w-60 -translate-x-1/2 rounded-md border border-[var(--forest)] bg-white p-2 shadow-[4px_4px_0_var(--lime)]"
                >
                  <p className="border-b border-[var(--forest)]/15 px-3 py-2 text-xs font-bold tracking-[.1em] text-[var(--forest)]/55 uppercase">
                    Мои питомцы
                  </p>
                  <div className="mt-1 max-h-64 overflow-y-auto">
                    {pets.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        role="option"
                        aria-selected={pet.id === item.id}
                        onClick={() => choose(item)}
                        className={`flex w-full items-center justify-between gap-3 rounded-sm px-3 py-2.5 text-left text-sm font-semibold transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] ${
                          pet.id === item.id
                            ? 'bg-[var(--cream)] text-[var(--forest)]'
                            : 'text-[var(--ink)]/70'
                        }`}
                      >
                        <span className="truncate">
                          {item.name}
                        </span>
                        {pet.id === item.id ? (
                          <span aria-hidden="true">✓</span>
                        ) : null}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </>
          ) : (
            <span className="hidden text-sm font-semibold text-[var(--ink)]/55 sm:inline">
              Питомец не выбран
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div
            ref={notificationsMenuRef}
            className="relative"
          >
            <button
              type="button"
              onClick={() => {
                setNotificationsOpen((value) => !value);
                setPetsOpen(false);
                setProfileOpen(false);
              }}
              aria-expanded={notificationsOpen}
              aria-haspopup="dialog"
              aria-label="Ближайшие события"
              title="Ближайшие события"
              className="grid size-10 place-items-center rounded-md border border-[var(--forest)]/55 bg-white text-[var(--forest)] transition-colors hover:bg-[var(--cream)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
            >
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
                <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
                <path d="M10 21h4" />
              </svg>
            </button>
            {notificationsOpen ? (
              <section
                role="dialog"
                aria-label="Ближайшие события"
                className="absolute right-0 top-[calc(100%+.65rem)] z-40 w-80 rounded-md border border-[var(--forest)] bg-white p-2 shadow-[4px_4px_0_var(--lime)] sm:w-96"
              >
                <div className="border-b border-[var(--forest)]/15 px-3 py-3">
                  <h2 className="text-sm font-black text-[var(--forest)]">
                    Ближайшие события
                  </h2>
                  <p className="mt-0.5 text-sm text-[var(--ink)]/60">
                    На ближайшие 30 дней
                  </p>
                </div>
                <div className="max-h-80 divide-y divide-[var(--forest)]/10 overflow-y-auto">
                  {upcomingEvents.isPending ? (
                    <p className="px-3 py-5 text-sm text-[var(--ink)]/60">
                      Загружаем события…
                    </p>
                  ) : upcomingEvents.isError ? (
                    <p className="px-3 py-5 text-sm text-red-800">
                      Не удалось загрузить события.
                    </p>
                  ) : upcomingEvents.data?.items.length ? (
                    upcomingEvents.data.items.map(
                      (event) => (
                        <div
                          key={event.id}
                          className="border-l-2 px-3 py-3"
                          style={{
                            borderLeftColor:
                              petColorById.get(event.petId),
                          }}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <p className="font-bold text-[var(--forest)]">
                              {event.name}
                            </p>
                            {event.isOverdue ? (
                              <span className="shrink-0 rounded-sm bg-red-50 px-1.5 py-0.5 text-xs font-bold text-red-800">
                                Просрочено
                              </span>
                            ) : null}
                          </div>
                          <p className="mt-1 inline-flex items-center gap-1 text-xs font-bold text-[var(--ink)]/65">
                            <span
                              aria-hidden="true"
                              className="size-2 rounded-full"
                              style={{
                                backgroundColor:
                                  petColorById.get(
                                    event.petId,
                                  ),
                              }}
                            />
                            {petNameById.get(event.petId) ??
                              'Питомец'}
                          </p>
                          <p className="mt-1 text-sm text-[var(--ink)]/60">
                            {formatDate(event.schedule)}
                          </p>
                        </div>
                      ),
                    )
                  ) : (
                    <p className="px-3 py-5 text-sm text-[var(--ink)]/60">
                      Ближайших событий нет.
                    </p>
                  )}
                </div>
              </section>
            ) : null}
          </div>
          <div ref={profileMenuRef} className="relative">
            <button
              type="button"
              onClick={() => {
                setProfileOpen((value) => !value);
                setPetsOpen(false);
                setNotificationsOpen(false);
              }}
              aria-expanded={profileOpen}
              aria-haspopup="menu"
              className="grid h-10 grid-cols-[auto_minmax(0,1fr)_1.25rem] items-center gap-2 rounded-md border border-[var(--forest)]/55 bg-white px-2 text-sm font-bold text-[var(--forest)] transition-colors hover:bg-[var(--cream)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
            >
              <span className="grid size-7 place-items-center rounded-full bg-[var(--forest)] text-xs text-white">
                {user?.fullName
                  ?.slice(0, 1)
                  .toUpperCase() ?? 'P'}
              </span>
              <span className="hidden max-w-28 truncate leading-none md:inline">
                {user?.fullName ?? 'Профиль'}
              </span>
              <ChevronDown />
            </button>
            {profileOpen ? (
              <div
                role="menu"
                aria-label="Профиль"
                className="absolute right-0 top-[calc(100%+.65rem)] z-40 w-60 rounded-md border border-[var(--forest)] bg-white p-2 shadow-[4px_4px_0_var(--lime)]"
              >
                <div className="border-b border-[var(--forest)]/15 px-3 py-3">
                  <p className="text-sm font-bold text-[var(--forest)]">
                    {user?.fullName ?? 'Профиль'}
                  </p>
                  <p className="mt-0.5 truncate text-sm text-[var(--ink)]/60">
                    @{user?.login ?? 'user'}
                  </p>
                </div>
                <Link
                  href="/account"
                  role="menuitem"
                  onClick={() => setProfileOpen(false)}
                  className="mt-2 flex w-full items-center justify-between rounded-sm px-3 py-2.5 text-left text-sm font-semibold text-[var(--forest)] transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
                >
                  <span className="flex items-center gap-2">
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
                      <circle cx="12" cy="8" r="3" />
                      <path d="M5 20a7 7 0 0 1 14 0" />
                    </svg>
                    Личный кабинет
                  </span>
                  <span aria-hidden="true">→</span>
                </Link>
                <button
                  type="button"
                  role="menuitem"
                  disabled={logout.isPending}
                  onClick={() => logout.mutate()}
                  className="mt-2 flex w-full items-center justify-between rounded-sm px-3 py-2.5 text-left text-sm font-semibold text-[var(--forest)] transition-colors hover:bg-[var(--lime)] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <span>
                    {logout.isPending
                      ? 'Выходим…'
                      : 'Выйти'}
                  </span>
                  <span aria-hidden="true">↗</span>
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </header>
      <DashboardSidebar
        activeTool={tool}
        hasPet={Boolean(pet)}
        onToolChange={(next) => {
          setReminderEvent(undefined);
          setTool(next);
        }}
      />
      <main className="p-5 sm:p-8 lg:p-10">
        {petsQuery.isPending ? (
          'Загружаем питомцев…'
        ) : !pet ? (
          <section className="mx-auto max-w-xl rounded-md border-2 border-[var(--forest)] bg-white p-8 shadow-[6px_6px_0_var(--lime)]">
            <h1 className="text-3xl font-black text-[var(--forest)]">
              Добавьте первого питомца
            </h1>
            <p className="mt-3 text-[var(--ink)]/70">
              Создайте профиль, чтобы вести историю
              здоровья, питания и напоминаний.
            </p>
            <motion.button
              onClick={() => setDialog('create')}
              initial="rest"
              animate="rest"
              whileHover={reduced ? 'rest' : 'hover'}
              className="mt-6 rounded-sm bg-[var(--forest)] px-5 py-3 font-bold text-white"
            >
              <motion.span
                variants={{
                  rest: { rotate: 0 },
                  hover: { rotate: 90 },
                }}
                className="mr-2 inline-block"
              >
                ＋
              </motion.span>
              Добавить питомца
            </motion.button>
          </section>
        ) : tool === 'home' ? (
          <PetHome
            key={pet.id}
            pet={pet}
            onCreate={() => setDialog('create')}
            onEdit={() => setDialog('edit')}
            onDelete={() => setDialog('delete')}
          />
        ) : tool === 'health' ? (
          <HealthPanel
            key={pet.id}
            pet={pet}
            onOpenReminders={(event) => {
              setReminderEvent(event);
              setTool('reminders');
            }}
          />
        ) : tool === 'food' ? (
          <FoodPanel
            key={pet.id}
            pet={pet}
            onOpenReminders={() => {
              setReminderEvent(undefined);
              setTool('reminders');
            }}
          />
        ) : tool === 'reminders' ? (
          <CareCalendar
            key={pet.id}
            focusEvent={reminderEvent}
            petId={pet.id}
          />
        ) : (
          <Panel pet={pet} tool={tool} />
        )}
      </main>
      {dialog === 'create' ? (
        <PetModal
          title="Добавить питомца"
          close={() => setDialog(null)}
        >
          <CreatePetForm
            onSuccess={(item) => {
              setSelectedId(item.id);
              setTool('home');
              setDialog(null);
            }}
          />
        </PetModal>
      ) : null}
      {dialog === 'edit' && pet ? (
        <PetModal
          title="Изменить данные"
          close={() => setDialog(null)}
        >
          <EditPetForm
            pet={pet}
            onSuccess={() => setDialog(null)}
          />
        </PetModal>
      ) : null}
      {dialog === 'delete' && pet ? (
        <PetModal
          title="Удалить питомца?"
          close={() => setDialog(null)}
        >
          <p>
            Профиль «{pet.name}» будет удалён. Это действие
            нельзя отменить.
          </p>
          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={() => setDialog(null)}
              className="rounded-sm border border-[var(--forest)] px-4 py-2"
            >
              Отмена
            </button>
            <button
              disabled={deletion.isPending}
              onClick={() =>
                deletion.mutate(pet.id, {
                  onSuccess: () => {
                    setSelectedId(null);
                    setDialog(null);
                  },
                })
              }
              className="rounded-sm bg-red-800 px-4 py-2 text-white"
            >
              Удалить
            </button>
          </div>
        </PetModal>
      ) : null}
      <ReminderToast />
    </div>
  );
}
