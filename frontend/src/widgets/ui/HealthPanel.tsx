'use client';

import { useGetCategoriesQuery } from '@src/entities/category';
import {
  type Event,
  type EventType,
  eventPeriodLabels,
  eventStatusLabels,
  eventTypeLabels,
  useGetEventsQuery,
} from '@src/entities/event';
import type { Pet } from '@src/entities/pet';
import { useGetStatesQuery } from '@src/entities/state';
import { CreateHealthEventForm } from '@src/features/event/create-event';
import { AddWeightForm } from '@src/features/state/create-state';
import { Uid } from '@src/shared/api/global.types';
import { useMemo, useState } from 'react';

// System category seeded by the backend for weight measurements, in grams.
const WEIGHT_CATEGORY_NAME = 'Вес';

type EntryType = EventType | 'weight';

type HealthEntry =
  | {
      kind: 'event';
      id: Uid;
      time: number;
      event: Event;
    }
  | {
      kind: 'weight';
      id: Uid;
      time: number;
      grams: number;
      delta: number | null;
    };

const entryTypes: EntryType[] = [
  'vet_visit',
  'vaccination',
  'parasite_treatment',
  'weight',
  'medication',
  'grooming',
  'other',
];

const entryLabel = (type: EntryType) =>
  type === 'weight' ? 'Взвешивание' : eventTypeLabels[type];

const entryTypeOf = (entry: HealthEntry): EntryType =>
  entry.kind === 'weight' ? 'weight' : entry.event.type;

const weightFormatter = new Intl.NumberFormat('ru-RU', {
  maximumFractionDigits: 2,
});
const formatWeight = (grams: number) =>
  grams >= 1000
    ? `${weightFormatter.format(grams / 1000)} кг`
    : `${grams} г`;
const formatDelta = (grams: number) =>
  `${grams > 0 ? '+' : grams < 0 ? '−' : '±'}${formatWeight(Math.abs(grams))}`;

const dayFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
});
const monthFormatter = new Intl.DateTimeFormat('ru-RU', {
  month: 'short',
});

const chipClassName =
  'inline-flex cursor-pointer items-center rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-semibold text-[var(--ink)]/75 transition-colors hover:border-[var(--forest)] hover:text-[var(--forest)] aria-pressed:border-[var(--forest)] aria-pressed:bg-[var(--lime)] aria-pressed:text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]';
const badgeClassName =
  'inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-semibold';

function DateMark({ time }: { time: number }) {
  const date = new Date(time * 1000);
  const isThisYear =
    date.getFullYear() === new Date().getFullYear();

  return (
    <time
      dateTime={date.toISOString()}
      className="pt-0.5 text-center leading-none"
    >
      <span className="block text-2xl font-black text-[var(--forest)]">
        {dayFormatter.format(date)}
      </span>
      <span className="mt-1 block text-xs font-semibold text-[var(--ink)]/55">
        {monthFormatter.format(date)}
      </span>
      {isThisYear ? null : (
        <span className="mt-0.5 block text-xs text-[var(--ink)]/45">
          {date.getFullYear()}
        </span>
      )}
    </time>
  );
}

function EventBadges({ event }: { event: Event }) {
  const isPlanned = event.status === 'planned';

  if (!isPlanned && event.status !== 'done') {
    return (
      <span
        className={`${badgeClassName} border-[var(--ink)]/20 text-[var(--ink)]/55`}
      >
        {eventStatusLabels[event.status]}
      </span>
    );
  }

  return (
    <>
      {event.isOverdue ? (
        <span
          className={`${badgeClassName} border-red-800/40 bg-red-50 text-red-800`}
        >
          Просрочено
        </span>
      ) : isPlanned ? (
        <span
          className={`${badgeClassName} border-[var(--forest)]/30 bg-[var(--cream)] text-[var(--forest)]`}
        >
          {eventStatusLabels.planned}
        </span>
      ) : null}
      {event.period !== 'none' ? (
        <span
          className={`${badgeClassName} border-[var(--forest)]/20 text-[var(--forest)]/75`}
        >
          <span aria-hidden="true" className="mr-1">
            ↻
          </span>
          {eventPeriodLabels[event.period]}
        </span>
      ) : null}
    </>
  );
}

function HealthEntryItem({
  entry,
}: {
  entry: HealthEntry;
}) {
  return (
    <li className="grid grid-cols-[3rem_minmax(0,1fr)] gap-4 border-b border-[var(--forest)]/10 py-4 last:border-b-0">
      <DateMark time={entry.time} />
      <div className="min-w-0">
        <p className="text-xs font-semibold text-[var(--forest)]/60">
          {entryLabel(entryTypeOf(entry))}
        </p>
        {entry.kind === 'weight' ? (
          <p className="mt-0.5 font-bold text-[var(--ink)]">
            {formatWeight(entry.grams)}
            {entry.delta !== null ? (
              <span className="ml-2 text-sm font-semibold text-[var(--ink)]/55">
                {formatDelta(entry.delta)}
              </span>
            ) : null}
          </p>
        ) : (
          <>
            <p className="mt-0.5 font-bold break-words text-[var(--ink)]">
              {entry.event.name}
            </p>
            {entry.event.description ? (
              <p className="mt-2 border-l-2 border-[var(--lime)] pl-3 text-sm leading-6 break-words whitespace-pre-line text-[var(--ink)]/70">
                {entry.event.description}
              </p>
            ) : null}
            <div className="mt-2 flex flex-wrap gap-1.5 empty:hidden">
              <EventBadges event={entry.event} />
            </div>
          </>
        )}
      </div>
    </li>
  );
}

function HealthBoard({
  pet,
  weightCategoryId,
}: {
  pet: Pet;
  weightCategoryId: Uid | null;
}) {
  const [entryType, setEntryType] =
    useState<EntryType | null>(null);
  const [filter, setFilter] = useState<EntryType | 'all'>(
    'all',
  );
  const [savedLabel, setSavedLabel] = useState<
    string | null
  >(null);
  const events = useGetEventsQuery({
    page: 0,
    size: 100,
    petId: pet.id,
  });
  const weights = useGetStatesQuery({
    page: 0,
    size: 100,
    petId: pet.id,
    categoryId: weightCategoryId ?? undefined,
  });

  const eventItems = events.data?.items;
  const stateItems = weights.data?.items;
  const entries = useMemo(() => {
    // States come newest first, so the next item is the previous weighing.
    const weightStates = (stateItems ?? []).filter(
      (state) => state.categoryId === weightCategoryId,
    );
    const result: HealthEntry[] = [
      ...weightStates.map((state, index): HealthEntry => ({
        kind: 'weight',
        id: state.id,
        time: state.time,
        grams: state.value,
        delta: weightStates[index + 1]
          ? state.value - weightStates[index + 1].value
          : null,
      })),
      ...(eventItems ?? []).map((event): HealthEntry => ({
        kind: 'event',
        id: event.id,
        time: event.schedule,
        event,
      })),
    ];
    return result.sort((a, b) => b.time - a.time);
  }, [eventItems, stateItems, weightCategoryId]);

  const presentTypes = entryTypes.filter((type) =>
    entries.some((entry) => entryTypeOf(entry) === type),
  );
  const visible =
    filter === 'all'
      ? entries
      : entries.filter(
          (entry) => entryTypeOf(entry) === filter,
        );
  const latestWeight = entries.find(
    (entry) => entry.kind === 'weight',
  );

  const finish = (label: string) => {
    setSavedLabel(label);
    setEntryType(null);
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_.8fr] xl:items-start">
      <section
        aria-labelledby="health-history-title"
        className="order-2 rounded-md border-2 border-[var(--forest)] bg-white p-5 shadow-[4px_4px_0_var(--lime)] xl:order-1"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2
              id="health-history-title"
              className="text-xl font-black text-[var(--forest)]"
            >
              Карта здоровья
            </h2>
            <p className="mt-1 text-sm text-[var(--ink)]/60">
              {pet.name}: прививки, обработки, визиты к
              врачу и взвешивания
            </p>
          </div>
          {latestWeight?.kind === 'weight' ? (
            <div className="rounded-sm bg-[var(--cream)] px-3 py-2 text-right">
              <p className="text-xs text-[var(--ink)]/55">
                Последний вес
              </p>
              <p className="text-xl font-black text-[var(--forest)]">
                {formatWeight(latestWeight.grams)}
              </p>
              {latestWeight.delta !== null ? (
                <p className="text-xs text-[var(--ink)]/60">
                  {formatDelta(latestWeight.delta)} с
                  прошлого раза
                </p>
              ) : null}
            </div>
          ) : null}
        </div>

        {presentTypes.length > 1 ? (
          <div
            role="group"
            aria-label="Фильтр по типу записи"
            className="mt-5 flex flex-wrap gap-2"
          >
            <button
              type="button"
              aria-pressed={filter === 'all'}
              onClick={() => setFilter('all')}
              className={chipClassName}
            >
              Все
            </button>
            {presentTypes.map((type) => (
              <button
                key={type}
                type="button"
                aria-pressed={filter === type}
                onClick={() => setFilter(type)}
                className={chipClassName}
              >
                {entryLabel(type)}
              </button>
            ))}
          </div>
        ) : null}

        {events.isPending || weights.isPending ? (
          <p className="py-6 text-sm text-[var(--ink)]/60">
            Загружаем историю…
          </p>
        ) : events.isError || weights.isError ? (
          <p
            role="alert"
            className="mt-5 border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
          >
            Не удалось загрузить историю. Обновите страницу.
          </p>
        ) : visible.length ? (
          <ol className="mt-3">
            {visible.map((entry) => (
              <HealthEntryItem
                key={`${entry.kind}-${entry.id}`}
                entry={entry}
              />
            ))}
          </ol>
        ) : (
          <p className="py-6 text-sm text-[var(--ink)]/60">
            Пока нет записей. Добавьте первую: визит к
            врачу, прививку или взвешивание.
          </p>
        )}
      </section>

      <section
        aria-labelledby="health-entry-title"
        className="order-1 rounded-md border border-[var(--forest)]/25 bg-white p-5 xl:order-2"
      >
        <h2
          id="health-entry-title"
          className="text-xl font-black text-[var(--forest)]"
        >
          Новая запись
        </h2>
        <p className="mt-1 text-sm text-[var(--ink)]/60">
          Выберите, что добавить
        </p>
        <div
          role="group"
          aria-label="Тип записи"
          className="mt-4 flex flex-wrap gap-2"
        >
          {entryTypes.map((type) => (
            <button
              key={type}
              type="button"
              aria-pressed={entryType === type}
              onClick={() => {
                setSavedLabel(null);
                setEntryType((current) =>
                  current === type ? null : type,
                );
              }}
              className={chipClassName}
            >
              {entryLabel(type)}
            </button>
          ))}
        </div>

        {savedLabel ? (
          <p
            role="status"
            className="mt-4 border-l-4 border-[var(--forest)] bg-[var(--lime)]/40 px-4 py-3 text-sm font-semibold text-[var(--forest)]"
          >
            {savedLabel} — сохранено в карте здоровья
          </p>
        ) : null}

        {entryType ? (
          <div className="mt-5 border-t border-[var(--forest)]/15 pt-5">
            {entryType !== 'weight' ? (
              <CreateHealthEventForm
                key={entryType}
                petId={pet.id}
                type={entryType}
                onSuccess={(event) => finish(event.name)}
              />
            ) : weightCategoryId ? (
              <AddWeightForm
                petId={pet.id}
                categoryId={weightCategoryId}
                onSuccess={(state) =>
                  finish(`Вес ${formatWeight(state.value)}`)
                }
              />
            ) : (
              <p
                role="alert"
                className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
              >
                Не найдена категория «{WEIGHT_CATEGORY_NAME}
                ». Взвешивание пока недоступно.
              </p>
            )}
          </div>
        ) : null}
      </section>
    </div>
  );
}

export function HealthPanel({ pet }: { pet: Pet }) {
  const categories = useGetCategoriesQuery({
    page: 0,
    size: 20,
    q: WEIGHT_CATEGORY_NAME,
  });

  if (categories.isPending) {
    return (
      <p className="text-sm text-[var(--ink)]/60">
        Загружаем карту здоровья…
      </p>
    );
  }

  const weightCategory = categories.data?.items.find(
    (item) => item.name === WEIGHT_CATEGORY_NAME,
  );

  return (
    <HealthBoard
      pet={pet}
      weightCategoryId={weightCategory?.id ?? null}
    />
  );
}
