'use client';

import {
  type Event,
  type EventPeriod,
  type EventType,
  useGetEventsQuery,
} from '@src/entities/event';
import { useGetPetQuery } from '@src/entities/pet';
import { useCreateEventMutation } from '@src/features/event/create-event';
import { useDownloadCalendarMutation } from '@src/features/event/download-calendar';
import { CreateNotificationForm } from '@src/features/notification/create-notification/ui/CreateNotificationForm';
import { createPetColorMap } from '@src/shared/lib';
import { Dialog } from '@src/shared/ui';
import { useCallback, useMemo, useState } from 'react';

import {
  EventNotificationsButton,
  EventNotificationsDialog,
} from './EventNotifications';

const monthFormatter = new Intl.DateTimeFormat('ru-RU', {
  month: 'long',
});
const fullDateFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});
const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

const eventTypes: Array<{
  value: EventType;
  label: string;
}> = [
  { value: 'vaccination', label: 'Вакцинация' },
  {
    value: 'parasite_treatment',
    label: 'Обработка от паразитов',
  },
  { value: 'vet_visit', label: 'Визит к ветеринару' },
  { value: 'medication', label: 'Приём лекарства' },
  { value: 'grooming', label: 'Груминг' },
  { value: 'other', label: 'Другое' },
];

const periods: Array<{
  value: EventPeriod;
  label: string;
}> = [
  { value: 'none', label: 'Не повторять' },
  { value: 'daily', label: 'Каждый день' },
  { value: 'weekly', label: 'Каждую неделю' },
  { value: 'monthly', label: 'Каждый месяц' },
  { value: 'quarterly', label: 'Раз в квартал' },
  { value: 'half_year', label: 'Раз в полгода' },
  { value: 'yearly', label: 'Каждый год' },
];

interface EventFormValues {
  description: string;
  name: string;
  period: EventPeriod;
  petId: string;
  type: EventType;
}

const dateKey = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;

const startOfDay = (date: Date) =>
  new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
  );

const CALENDAR_UNTIL_DEFAULT_DAYS = 365;
const CALENDAR_UNTIL_MAX_DAYS = 1826;

const inputClasses =
  'mt-1.5 w-full rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-2.5 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)] focus:ring-2 focus:ring-[var(--lime)]';

function Icon({ children }: { children: React.ReactNode }) {
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

export function CareCalendar({
  focusEvent,
  petId,
}: {
  focusEvent?: Event;
  petId?: string;
}) {
  const now = new Date();
  const initialDate = focusEvent
    ? new Date(focusEvent.schedule * 1000)
    : now;
  const [visibleDate, setVisibleDate] = useState(
    () =>
      new Date(
        initialDate.getFullYear(),
        initialDate.getMonth(),
        1,
      ),
  );
  const [selectedDate, setSelectedDate] = useState(() =>
    startOfDay(initialDate),
  );
  const [listEvent, setListEvent] = useState<Event | null>(
    focusEvent ?? null,
  );
  const closeList = useCallback(
    () => setListEvent(null),
    [],
  );
  const [isCreateOpen, setCreateOpen] = useState(false);
  const [isDownloadOpen, setDownloadOpen] = useState(false);
  const [notificationEvent, setNotificationEvent] =
    useState<Event | null>(null);
  const petsQuery = useGetPetQuery({ page: 0, size: 100 });
  const pets = (petsQuery.data?.items ?? []).filter(
    (pet) => !petId || pet.id === petId,
  );
  const rangeStart = new Date(
    visibleDate.getFullYear(),
    visibleDate.getMonth(),
    1,
  );
  const rangeEnd = new Date(
    visibleDate.getFullYear(),
    visibleDate.getMonth() + 1,
    1,
  );
  const eventsQuery = useGetEventsQuery({
    page: 0,
    size: 100,
    petId,
    from: rangeStart.getTime() / 1000,
    to: rangeEnd.getTime() / 1000 - 1,
  });
  const petColorById = useMemo(
    () => createPetColorMap(pets.map((pet) => pet.id)),
    [pets],
  );
  const petNameById = useMemo(
    () => new Map(pets.map((pet) => [pet.id, pet.name])),
    [pets],
  );
  const eventsByDate = useMemo(() => {
    const result = new Map<
      string,
      { count: number; petIds: Set<string> }
    >();
    eventsQuery.data?.items.forEach((event) => {
      const key = dateKey(new Date(event.schedule * 1000));
      const eventsForDay = result.get(key) ?? {
        count: 0,
        petIds: new Set<string>(),
      };
      eventsForDay.count += 1;
      eventsForDay.petIds.add(event.petId);
      result.set(key, eventsForDay);
    });
    return result;
  }, [eventsQuery.data?.items]);
  const selectedEvents = useMemo(
    () =>
      eventsQuery.data?.items.filter(
        (event) =>
          dateKey(new Date(event.schedule * 1000)) ===
          dateKey(selectedDate),
      ) ?? [],
    [eventsQuery.data?.items, selectedDate],
  );

  const days = useMemo(() => {
    const monthStart = new Date(
      visibleDate.getFullYear(),
      visibleDate.getMonth(),
      1,
    );
    const startOffset = (monthStart.getDay() + 6) % 7;
    const count = new Date(
      visibleDate.getFullYear(),
      visibleDate.getMonth() + 1,
      0,
    ).getDate();
    return Array.from(
      { length: startOffset + count },
      (_, index) =>
        index < startOffset
          ? null
          : new Date(
              visibleDate.getFullYear(),
              visibleDate.getMonth(),
              index - startOffset + 1,
            ),
    );
  }, [visibleDate]);

  const years = Array.from(
    { length: 9 },
    (_, index) => now.getFullYear() - 4 + index,
  );
  const setMonth = (month: number) => {
    const next = new Date(
      visibleDate.getFullYear(),
      month,
      1,
    );
    setVisibleDate(next);
    setSelectedDate(next);
  };
  const setYear = (year: number) => {
    const next = new Date(year, visibleDate.getMonth(), 1);
    setVisibleDate(next);
    setSelectedDate(next);
  };
  const moveMonth = (amount: number) => {
    const next = new Date(
      visibleDate.getFullYear(),
      visibleDate.getMonth() + amount,
      1,
    );
    setVisibleDate(next);
    setSelectedDate(next);
  };

  if (petsQuery.isPending) {
    return (
      <p className="text-sm text-[var(--ink)]/60">
        Загружаем календарь…
      </p>
    );
  }

  if (!pets.length) {
    return (
      <div className="max-w-xl border-l-4 border-[var(--lime)] pl-5">
        <h2 className="text-2xl font-black text-[var(--forest)]">
          Календарь заботы
        </h2>
        <p className="mt-3 leading-6 text-[var(--ink)]/65">
          Сначала добавьте питомца на дашборде — каждое
          напоминание привязано к его профилю.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--forest)]/15 pb-5">
        <div>
          <p className="text-sm font-semibold text-[var(--ink)]/55">
            План ухода и напоминания
          </p>
          <h2 className="mt-1 text-2xl font-black text-[var(--forest)] sm:text-3xl">
            Календарь заботы
          </h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setDownloadOpen(true)}
            className="inline-flex items-center gap-2 rounded-sm border border-[var(--forest)]/25 bg-white px-4 py-2.5 text-sm font-bold text-[var(--forest)] transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
          >
            <Icon>
              <path d="M12 4v11M7 10l5 5 5-5M5 20h14" />
            </Icon>
            Скачать .ics
          </button>
          <button
            type="button"
            onClick={() => setCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-sm bg-[var(--forest)] px-4 py-2.5 text-sm font-bold text-white transition-colors hover:bg-[var(--forest)]/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
          >
            <Icon>
              <path d="M12 5v14M5 12h14" />
            </Icon>
            Добавить событие
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-7 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <section aria-label="Календарь событий">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => moveMonth(-1)}
                aria-label="Предыдущий месяц"
                className="grid size-9 place-items-center rounded-full border border-[var(--forest)]/25 text-[var(--forest)] transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
              >
                <Icon>
                  <path d="m15 18-6-6 6-6" />
                </Icon>
              </button>
              <button
                type="button"
                onClick={() => moveMonth(1)}
                aria-label="Следующий месяц"
                className="grid size-9 place-items-center rounded-full border border-[var(--forest)]/25 text-[var(--forest)] transition-colors hover:bg-[var(--lime)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
              >
                <Icon>
                  <path d="m9 18 6-6-6-6" />
                </Icon>
              </button>
            </div>
            <div className="flex gap-2">
              <label
                className="sr-only"
                htmlFor="calendar-month"
              >
                Месяц
              </label>
              <select
                id="calendar-month"
                value={visibleDate.getMonth()}
                onChange={(event) =>
                  setMonth(Number(event.target.value))
                }
                className="rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
              >
                {Array.from({ length: 12 }, (_, month) => (
                  <option key={month} value={month}>
                    {monthFormatter.format(
                      new Date(2026, month, 1),
                    )}
                  </option>
                ))}
              </select>
              <label
                className="sr-only"
                htmlFor="calendar-year"
              >
                Год
              </label>
              <select
                id="calendar-year"
                value={visibleDate.getFullYear()}
                onChange={(event) =>
                  setYear(Number(event.target.value))
                }
                className="rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div
            className="mt-5 grid grid-cols-7 gap-y-2"
            role="grid"
            aria-label={`${monthFormatter.format(visibleDate)} ${visibleDate.getFullYear()}`}
          >
            {weekdays.map((weekday) => (
              <div
                key={weekday}
                className="pb-2 text-center text-xs font-bold text-[var(--ink)]/45"
              >
                {weekday}
              </div>
            ))}
            {days.map((date, index) => {
              if (!date)
                return (
                  <div
                    key={`gap-${index}`}
                    aria-hidden="true"
                  />
                );
              const key = dateKey(date);
              const isSelected =
                key === dateKey(selectedDate);
              const isToday = key === dateKey(now);
              const eventsForDay = eventsByDate.get(key);
              const eventPetIds = eventsForDay?.petIds;
              const eventCount = eventsForDay?.count ?? 0;
              return (
                <div
                  key={key}
                  className="flex justify-center py-1"
                >
                  <button
                    type="button"
                    onClick={() => setSelectedDate(date)}
                    aria-pressed={isSelected}
                    aria-label={`${fullDateFormatter.format(date)}${eventCount ? `, событий: ${eventCount}` : ''}`}
                    className={`relative grid size-10 place-items-center rounded-full text-sm font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] sm:size-11 ${isSelected ? 'bg-[var(--forest)] text-white' : isToday ? 'border-2 border-[var(--forest)] text-[var(--forest)]' : 'text-[var(--ink)] hover:bg-[var(--lime)]'}`}
                  >
                    <span>{date.getDate()}</span>
                    {eventPetIds ? (
                      <span
                        aria-hidden="true"
                        className="absolute bottom-1 flex max-w-8 items-center justify-center gap-0.5"
                      >
                        {[...eventPetIds].map((petId) => (
                          <span
                            key={petId}
                            className="size-1.5 rounded-full ring-1 ring-white"
                            style={{
                              backgroundColor:
                                petColorById.get(petId),
                            }}
                          />
                        ))}
                      </span>
                    ) : null}
                  </button>
                </div>
              );
            })}
          </div>
          {eventsQuery.isError ? (
            <p
              role="alert"
              className="mt-5 text-sm text-red-800"
            >
              Не удалось загрузить события. Попробуйте ещё
              раз.
            </p>
          ) : null}
        </section>

        <aside className="border-t border-[var(--forest)]/15 pt-5 lg:border-t-0 lg:border-l lg:pl-6 lg:pt-0">
          <p className="text-sm font-semibold text-[var(--ink)]/55">
            Выбрано
          </p>
          <h3 className="mt-1 text-lg font-black text-[var(--forest)]">
            {fullDateFormatter.format(selectedDate)}
          </h3>
          <div className="mt-5 space-y-3">
            {selectedEvents.length ? (
              selectedEvents.map((event) => (
                <article
                  key={event.id}
                  className="border-l-2 bg-[var(--cream)] px-3 py-3"
                  style={{
                    borderLeftColor: petColorById.get(
                      event.petId,
                    ),
                  }}
                >
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <p className="font-bold text-[var(--forest)]">
                      {event.name}
                    </p>
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-[var(--ink)]/65">
                      <span
                        aria-hidden="true"
                        className="size-2 rounded-full"
                        style={{
                          backgroundColor: petColorById.get(
                            event.petId,
                          ),
                        }}
                      />
                      {petNameById.get(event.petId) ??
                        'Питомец'}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-[var(--ink)]/60">
                    {eventTypes.find(
                      (item) => item.value === event.type,
                    )?.label ?? 'Событие'}{' '}
                    ·{' '}
                    {event.status === 'planned'
                      ? 'Запланировано'
                      : event.status}
                  </p>
                  {event.description ? (
                    <p className="mt-2 text-sm leading-5 text-[var(--ink)]/65">
                      {event.description}
                    </p>
                  ) : null}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setNotificationEvent(event)
                      }
                      className="rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-bold text-[var(--forest)] transition-colors hover:border-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
                    >
                      + Добавить напоминание
                    </button>
                    <EventNotificationsButton
                      event={event}
                    />
                  </div>
                </article>
              ))
            ) : (
              <p className="text-sm leading-6 text-[var(--ink)]/60">
                На этот день ничего не запланировано.
              </p>
            )}
          </div>
        </aside>
      </div>

      {isCreateOpen ? (
        <CreateEventDialog
          selectedDate={selectedDate}
          pets={pets}
          onClose={() => setCreateOpen(false)}
        />
      ) : null}

      {isDownloadOpen ? (
        <DownloadCalendarDialog
          petId={petId}
          onClose={() => setDownloadOpen(false)}
        />
      ) : null}

      {listEvent ? (
        <EventNotificationsDialog
          event={listEvent}
          onClose={closeList}
        />
      ) : null}

      {notificationEvent ? (
        <CreateNotificationDialog
          event={notificationEvent}
          onClose={() => setNotificationEvent(null)}
        />
      ) : null}
    </div>
  );
}

function DownloadCalendarDialog({
  petId,
  onClose,
}: {
  petId?: string;
  onClose: () => void;
}) {
  const downloadCalendar = useDownloadCalendarMutation();
  const today = startOfDay(new Date());
  const shiftDays = (days: number) =>
    dateKey(
      new Date(
        today.getFullYear(),
        today.getMonth(),
        today.getDate() + days,
      ),
    );
  // Backend accepts until in (now, now + 1826 days]; the chosen day is sent as its end.
  const minDate = shiftDays(0);
  const maxDate = shiftDays(CALENDAR_UNTIL_MAX_DAYS - 1);
  const [until, setUntil] = useState(() =>
    shiftDays(CALENDAR_UNTIL_DEFAULT_DAYS),
  );
  const [validationError, setValidationError] = useState<
    string | null
  >(null);
  const submit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    if (!until || until < minDate || until > maxDate) {
      setValidationError(
        'Выберите дату не раньше сегодня и не дальше чем через 5 лет.',
      );
      return;
    }
    setValidationError(null);
    const [year, month, day] = until.split('-').map(Number);
    downloadCalendar.mutate(
      {
        petId,
        until:
          new Date(year, month - 1, day + 1).getTime() /
            1000 -
          1,
      },
      { onSuccess: onClose },
    );
  };
  return (
    <Dialog
      labelledBy="download-calendar-title"
      onClose={onClose}
    >
      <div className="mx-auto w-xl max-w-full p-5 sm:p-6">
        <div className="flex items-start justify-between gap-4 border-b border-[var(--forest)]/15 pb-4">
          <div>
            <p className="text-sm font-semibold text-[var(--ink)]/55">
              Файл для календаря телефона
            </p>
            <h2
              id="download-calendar-title"
              className="mt-1 text-2xl font-black text-[var(--forest)]"
            >
              Скачать .ics
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть"
            className="grid size-9 place-items-center rounded-full border border-[var(--forest)]/25 text-lg hover:bg-[var(--lime)]"
          >
            ×
          </button>
        </div>
        <form
          onSubmit={submit}
          className="mt-5 space-y-4"
          noValidate
        >
          <label className="block text-sm font-bold text-[var(--forest)]">
            Повторять события до
            <input
              type="date"
              value={until}
              min={minDate}
              max={maxDate}
              onChange={(event) =>
                setUntil(event.target.value)
              }
              className={inputClasses}
            />
          </label>
          {validationError || downloadCalendar.error ? (
            <p
              role="alert"
              className="border-l-4 border-red-700 bg-red-50 px-3 py-2 text-sm text-red-800"
            >
              {validationError ??
                'Не удалось скачать календарь. Попробуйте ещё раз.'}
            </p>
          ) : null}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-sm px-4 py-2.5 text-sm font-bold text-[var(--forest)] hover:bg-[var(--cream)]"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={downloadCalendar.isPending}
              className="rounded-sm bg-[var(--forest)] px-4 py-2.5 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {downloadCalendar.isPending
                ? 'Скачиваем…'
                : 'Скачать'}
            </button>
          </div>
        </form>
      </div>
    </Dialog>
  );
}

function CreateNotificationDialog({
  event,
  onClose,
}: {
  event: Event;
  onClose: () => void;
}) {
  return (
    <Dialog
      labelledBy="create-notification-title"
      onClose={onClose}
    >
      <div className="mx-auto w-xl max-w-full p-5 sm:p-6">
        <div className="flex min-w-0 items-start justify-between gap-4 border-b border-[var(--forest)]/15 pb-4">
          <div className="min-w-0">
            <p className="break-words text-sm font-semibold text-[var(--ink)]/55">
              {event.name}
            </p>
            <h2
              id="create-notification-title"
              className="mt-1 break-words text-2xl font-black text-[var(--forest)]"
            >
              Новое уведомление
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть"
            className="grid size-9 shrink-0 place-items-center rounded-full border border-[var(--forest)]/25 text-lg hover:bg-[var(--lime)]"
          >
            ×
          </button>
        </div>
        <div className="mt-5">
          <CreateNotificationForm
            eventId={event.id}
            onSuccess={onClose}
          />
        </div>
      </div>
    </Dialog>
  );
}

function CreateEventDialog({
  selectedDate,
  pets,
  onClose,
}: {
  selectedDate: Date;
  pets: Array<{ id: string; name: string }>;
  onClose: () => void;
}) {
  const createEvent = useCreateEventMutation();
  const [values, setValues] = useState<EventFormValues>({
    description: '',
    name: '',
    period: 'none',
    petId: pets[0].id,
    type: 'other',
  });
  const [validationError, setValidationError] = useState<
    string | null
  >(null);
  const update = <Key extends keyof EventFormValues>(
    key: Key,
    value: EventFormValues[Key],
  ) =>
    setValues((current) => ({ ...current, [key]: value }));
  const submit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    if (!values.name.trim()) {
      setValidationError('Введите название события.');
      return;
    }
    createEvent.mutate(
      {
        ...values,
        name: values.name.trim(),
        description: values.description.trim() || null,
        status: 'planned',
        schedule:
          new Date(
            selectedDate.getFullYear(),
            selectedDate.getMonth(),
            selectedDate.getDate(),
            12,
          ).getTime() / 1000,
      },
      { onSuccess: onClose },
    );
  };
  return (
    <Dialog
      labelledBy="create-event-title"
      onClose={onClose}
    >
      <div className="mx-auto w-3xl max-w-full p-5 sm:p-6">
        <div className="flex min-w-0 items-start justify-between gap-4 border-b border-[var(--forest)]/15 pb-4">
          <div className="min-w-0">
            <p className="break-words text-sm font-semibold text-[var(--ink)]/55">
              {fullDateFormatter.format(selectedDate)}
            </p>
            <h2
              id="create-event-title"
              className="mt-1 break-words text-2xl font-black text-[var(--forest)]"
            >
              Новое событие
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть"
            className="grid size-9 shrink-0 place-items-center rounded-full border border-[var(--forest)]/25 text-lg hover:bg-[var(--lime)]"
          >
            ×
          </button>
        </div>
        <form
          onSubmit={submit}
          className="mt-5 space-y-4"
          noValidate
        >
          <label className="block text-sm font-bold text-[var(--forest)]">
            Питомец
            <select
              value={values.petId}
              onChange={(event) =>
                update('petId', event.target.value)
              }
              className={inputClasses}
            >
              {pets.map((pet) => (
                <option key={pet.id} value={pet.id}>
                  {pet.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-bold text-[var(--forest)]">
            Что запланировано?
            <input
              value={values.name}
              onChange={(event) =>
                update('name', event.target.value)
              }
              className={inputClasses}
              placeholder="Например, прививка"
              autoFocus
            />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-bold text-[var(--forest)]">
              Тип
              <select
                value={values.type}
                onChange={(event) =>
                  update(
                    'type',
                    event.target.value as EventType,
                  )
                }
                className={inputClasses}
              >
                {eventTypes.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-bold text-[var(--forest)]">
              Повторение
              <select
                value={values.period}
                onChange={(event) =>
                  update(
                    'period',
                    event.target.value as EventPeriod,
                  )
                }
                className={inputClasses}
              >
                {periods.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="block text-sm font-bold text-[var(--forest)]">
            Комментарий{' '}
            <span className="font-normal text-[var(--ink)]/55">
              (необязательно)
            </span>
            <textarea
              value={values.description}
              onChange={(event) =>
                update('description', event.target.value)
              }
              className={inputClasses}
              rows={3}
            />
          </label>
          {validationError || createEvent.error ? (
            <p
              role="alert"
              className="border-l-4 border-red-700 bg-red-50 px-3 py-2 text-sm text-red-800"
            >
              {validationError ??
                'Не удалось создать событие. Проверьте данные и повторите попытку.'}
            </p>
          ) : null}
          <div className="flex flex-wrap justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-sm px-4 py-2.5 text-sm font-bold text-[var(--forest)] hover:bg-[var(--cream)]"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={createEvent.isPending}
              className="rounded-sm bg-[var(--forest)] px-4 py-2.5 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {createEvent.isPending
                ? 'Сохраняем…'
                : 'Создать событие'}
            </button>
          </div>
        </form>
      </div>
    </Dialog>
  );
}
