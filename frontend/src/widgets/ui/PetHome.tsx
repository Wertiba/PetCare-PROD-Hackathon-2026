'use client';

import {
  type Category,
  useGetCategoriesQuery,
} from '@src/entities/category';
import {
  eventTypeLabels,
  useGetUpcomingEventsQuery,
} from '@src/entities/event';
import { useGetFoodsQuery } from '@src/entities/food';
import type { Pet } from '@src/entities/pet';
import { useGetStatesQuery } from '@src/entities/state';
import Image from 'next/image';
import { useMemo, useState } from 'react';

interface PetHomeProps {
  pet: Pet;
  onCreate: () => void;
  onDelete: () => void;
  onEdit: () => void;
}

const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
  dateStyle: 'long',
});
// Birth dates are stored as UTC midnight; in local time they would show the previous day west of UTC.
const birthDateFormatter = new Intl.DateTimeFormat(
  'ru-RU',
  {
    dateStyle: 'long',
    timeZone: 'UTC',
  },
);
const dateTimeFormatter = new Intl.DateTimeFormat('ru-RU', {
  dateStyle: 'medium',
  timeStyle: 'short',
});
const numberFormatter = new Intl.NumberFormat('ru-RU', {
  maximumFractionDigits: 2,
});
const WEIGHT_CATEGORY_NAME = 'Вес';

const unitLabels: Record<Category['unit'], string> = {
  none: '',
  g: 'г',
  ml: 'мл',
  min: 'мин',
  m: 'м',
  times: 'раз',
  rub: '₽',
  points: 'баллов',
};

function formatDate(value: number | null | undefined) {
  return value
    ? dateFormatter.format(new Date(value * 1000))
    : 'Не указана';
}

function formatDateTime(value: number) {
  return dateTimeFormatter.format(new Date(value * 1000));
}

function formatWeight(grams: number) {
  return `${numberFormatter.format(grams / 1000)} кг`;
}

function pluralize(
  value: number,
  forms: [string, string, string],
) {
  const lastTwoDigits = value % 100;
  const lastDigit = value % 10;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return forms[2];
  }
  if (lastDigit === 1) return forms[0];
  if (lastDigit >= 2 && lastDigit <= 4) return forms[1];
  return forms[2];
}

function formatMonthsAge(months: number | null) {
  if (months === null) return 'Не указан';

  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;
  const result = [];

  if (years) {
    result.push(
      `${years} ${pluralize(years, ['год', 'года', 'лет'])}`,
    );
  }
  if (remainingMonths || !years) {
    result.push(
      `${remainingMonths} ${pluralize(remainingMonths, [
        'месяц',
        'месяца',
        'месяцев',
      ])}`,
    );
  }

  return result.join(' ');
}

function formatAge(
  birthDate: number | null,
  ageMonths: number | null,
) {
  if (!birthDate) return formatMonthsAge(ageMonths);

  const sourceDate = new Date(birthDate * 1000);
  const born = new Date(
    sourceDate.getUTCFullYear(),
    sourceDate.getUTCMonth(),
    sourceDate.getUTCDate(),
  );
  const now = new Date();
  const today = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
  );

  if (born > today) return formatMonthsAge(ageMonths);

  const birthDay = born.getDate();
  const calendarDate = (year: number, month: number) =>
    new Date(
      year,
      month,
      Math.min(
        birthDay,
        new Date(year, month + 1, 0).getDate(),
      ),
    );

  let years = today.getFullYear() - born.getFullYear();
  if (
    today <
    calendarDate(today.getFullYear(), born.getMonth())
  ) {
    years -= 1;
  }

  const anniversaryYear = born.getFullYear() + years;
  let months = 0;
  for (let candidate = 1; candidate <= 11; candidate += 1) {
    if (
      calendarDate(
        anniversaryYear,
        born.getMonth() + candidate,
      ) <= today
    ) {
      months = candidate;
    } else {
      break;
    }
  }

  const anchor = calendarDate(
    anniversaryYear,
    born.getMonth() + months,
  );
  const days = Math.round(
    (Date.UTC(
      today.getFullYear(),
      today.getMonth(),
      today.getDate(),
    ) -
      Date.UTC(
        anchor.getFullYear(),
        anchor.getMonth(),
        anchor.getDate(),
      )) /
      86_400_000,
  );

  if (years) {
    return [
      `${years} ${pluralize(years, ['год', 'года', 'лет'])}`,
      months
        ? `${months} ${pluralize(months, [
            'месяц',
            'месяца',
            'месяцев',
          ])}`
        : null,
    ]
      .filter(Boolean)
      .join(' ');
  }

  if (months) {
    return [
      `${months} ${pluralize(months, [
        'месяц',
        'месяца',
        'месяцев',
      ])}`,
      days
        ? `${days} ${pluralize(days, ['день', 'дня', 'дней'])}`
        : null,
    ]
      .filter(Boolean)
      .join(' ');
  }

  return `${days} ${pluralize(days, ['день', 'дня', 'дней'])}`;
}

function ActionIcon({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <svg
      aria-hidden="true"
      className="size-5 shrink-0"
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

function EmptyLine({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <p className="py-8 text-sm leading-6 text-[var(--ink)]/55">
      {children}
    </p>
  );
}

export function PetHome({
  pet,
  onCreate,
  onDelete,
  onEdit,
}: PetHomeProps) {
  const [photoNotice, setPhotoNotice] = useState(false);
  const events = useGetUpcomingEventsQuery({
    days: 30,
    page: 0,
    size: 4,
    petId: pet.id,
  });
  const states = useGetStatesQuery({
    page: 0,
    size: 4,
    petId: pet.id,
  });
  const foods = useGetFoodsQuery({
    page: 0,
    size: 1,
    petId: pet.id,
  });
  const categories = useGetCategoriesQuery({
    page: 0,
    size: 100,
    q: '',
  });
  const weightCategories = useGetCategoriesQuery({
    page: 0,
    size: 20,
    q: WEIGHT_CATEGORY_NAME,
  });

  const categoryById = useMemo(
    () =>
      new Map(
        (categories.data?.items ?? []).map((category) => [
          category.id,
          category,
        ]),
      ),
    [categories.data?.items],
  );
  const latestFood = foods.data?.items[0];
  const weightCategory = weightCategories.data?.items.find(
    (category) => category.name === WEIGHT_CATEGORY_NAME,
  );

  return (
    <div className="mx-auto w-full max-w-[1600px]">
      <section className="grid overflow-hidden border-2 border-[var(--forest)] bg-white shadow-[6px_6px_0_var(--lime)] xl:grid-cols-[minmax(22rem,1.05fr)_minmax(28rem,1fr)]">
        <div className="relative min-h-[23rem] overflow-hidden bg-[var(--forest)] xl:min-h-[34rem]">
          <Image
            key={pet.photoUrl ?? 'placeholder'}
            src={pet.photoUrl ?? '/images/petcare-hero.png'}
            alt={
              pet.photoUrl
                ? `Фотография питомца ${pet.name}`
                : `Фотография-заглушка для питомца ${pet.name}`
            }
            fill
            priority
            unoptimized={Boolean(pet.photoUrl)}
            sizes="(min-width: 1280px) 45vw, 100vw"
            className="object-cover"
          />
          {!pet.photoUrl ? (
            <span className="absolute top-4 left-4 bg-[var(--cream)] px-3 py-1.5 text-xs font-bold text-[var(--forest)] shadow-[3px_3px_0_var(--lime)]">
              Фото пока не добавлено
            </span>
          ) : null}
          <button
            type="button"
            onClick={() => setPhotoNotice(true)}
            className="absolute right-4 bottom-4 inline-flex items-center gap-2 border-2 border-[var(--forest)] bg-white px-4 py-3 text-sm font-black text-[var(--forest)] shadow-[4px_4px_0_var(--lime)] transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-[2px_2px_0_var(--lime)] active:shadow-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            <ActionIcon>
              <path d="M14.5 6H20a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3.5L9 4h4l1.5 2Z" />
              <circle cx="12" cy="13" r="3" />
            </ActionIcon>
            Добавить фото
          </button>
        </div>

        <div className="flex flex-col p-6 sm:p-8 xl:p-10">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-sm font-semibold text-[var(--ink)]/55">
                {pet.animal?.name ?? 'Вид не указан'} ·{' '}
                {pet.breed?.name ?? 'порода не указана'}
              </p>
              <h1 className="mt-1 text-5xl leading-none font-black tracking-[-.04em] text-[var(--forest)] sm:text-6xl">
                {pet.name}
              </h1>
            </div>
            <span className="border border-[var(--forest)]/20 bg-[var(--cream)] px-3 py-2 text-sm font-bold text-[var(--forest)]">
              {formatAge(pet.birthDate, pet.ageMonths)}
            </span>
          </div>

          <dl className="mt-8 grid grid-cols-[minmax(8rem,.8fr)_minmax(0,1.2fr)] border-y border-[var(--forest)]/15 text-sm">
            {[
              ['Кличка', pet.name],
              ['Вид', pet.animal?.name ?? 'Не указан'],
              ['Порода', pet.breed?.name ?? 'Не указана'],
              [
                'Дата рождения',
                pet.birthDate
                  ? birthDateFormatter.format(
                      new Date(pet.birthDate * 1000),
                    )
                  : 'Не указана',
              ],
              [
                'Возраст',
                formatAge(pet.birthDate, pet.ageMonths),
              ],
              [
                'Фото',
                pet.photoUrl
                  ? 'Добавлено'
                  : 'Используется заглушка',
              ],
            ].map(([label, value]) => (
              <div
                key={label}
                className="col-span-2 grid grid-cols-subgrid border-b border-[var(--forest)]/10 py-2.5 last:border-b-0"
              >
                <dt className="text-[var(--ink)]/55">
                  {label}
                </dt>
                <dd
                  className="min-w-0 truncate font-semibold text-[var(--ink)]"
                  title={value}
                >
                  {value}
                </dd>
              </div>
            ))}
          </dl>

          {photoNotice ? (
            <p
              role="status"
              className="mt-5 border-l-4 border-[var(--forest)] bg-[var(--lime)]/35 px-4 py-3 text-sm font-semibold text-[var(--forest)]"
            >
              Загрузка дополнительных фото появится в
              следующем обновлении.
            </p>
          ) : null}

          <div className="mt-auto grid gap-2 pt-7 sm:grid-cols-2">
            <button
              type="button"
              onClick={onCreate}
              className="inline-flex min-h-12 items-center justify-center gap-2 bg-[var(--forest)] px-4 py-3 text-sm font-black text-white shadow-[4px_4px_0_var(--lime)] transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-[2px_2px_0_var(--lime)] active:shadow-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
            >
              <ActionIcon>
                <path d="M12 5v14M5 12h14" />
              </ActionIcon>
              Добавить питомца
            </button>
            <button
              type="button"
              onClick={onEdit}
              className="inline-flex min-h-12 items-center justify-center gap-2 border border-[var(--forest)] bg-white px-4 py-3 text-sm font-black text-[var(--forest)] transition-colors hover:bg-[var(--cream)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
            >
              <ActionIcon>
                <path d="m4 20 4.5-1 10-10a2.1 2.1 0 0 0-3-3l-10 10L4 20ZM13.5 8l3 3" />
              </ActionIcon>
              Изменить профиль
            </button>
            <button
              type="button"
              onClick={onDelete}
              className="inline-flex min-h-11 items-center justify-center gap-2 border border-red-800/35 px-4 py-2.5 text-sm font-bold text-red-800 transition-colors hover:bg-red-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-800 sm:col-span-2"
            >
              <ActionIcon>
                <path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5" />
              </ActionIcon>
              Удалить питомца
            </button>
          </div>
        </div>
      </section>

      <section className="mt-7 grid border-y border-[var(--forest)]/20 bg-white xl:grid-cols-3 xl:divide-x xl:divide-[var(--forest)]/15">
        <article className="p-5 sm:p-7">
          <div className="flex items-baseline justify-between gap-4">
            <h2 className="text-xl font-black text-[var(--forest)]">
              Ближайшие события
            </h2>
            <span className="text-xs font-bold text-[var(--forest)]/55">
              30 дней
            </span>
          </div>
          {events.isPending ? (
            <EmptyLine>Загружаем события…</EmptyLine>
          ) : events.data?.items.length ? (
            <ol className="mt-4 divide-y divide-[var(--forest)]/10">
              {events.data.items.map((event) => (
                <li
                  key={event.id}
                  className="grid grid-cols-[4.6rem_1fr] gap-3 py-3.5 first:pt-1"
                >
                  <time className="text-xs font-bold text-[var(--forest)]/60">
                    {formatDate(event.schedule)}
                  </time>
                  <div className="min-w-0">
                    <p className="truncate font-bold text-[var(--ink)]">
                      {event.name}
                    </p>
                    <p className="mt-0.5 text-xs text-[var(--ink)]/50">
                      {eventTypeLabels[event.type]}
                      {event.isOverdue
                        ? ' · Просрочено'
                        : ''}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyLine>
              На ближайшие 30 дней событий нет.
            </EmptyLine>
          )}
        </article>

        <article className="border-t border-[var(--forest)]/15 p-5 sm:p-7 xl:border-t-0">
          <h2 className="text-xl font-black text-[var(--forest)]">
            Последние измерения
          </h2>
          {states.isPending ||
          categories.isPending ||
          weightCategories.isPending ? (
            <EmptyLine>Загружаем измерения…</EmptyLine>
          ) : states.data?.items.length ? (
            <ol className="mt-4 divide-y divide-[var(--forest)]/10">
              {states.data.items.map((state) => {
                const category = categoryById.get(
                  state.categoryId,
                );
                const isWeight =
                  state.categoryId === weightCategory?.id;
                return (
                  <li
                    key={state.id}
                    className="flex items-center justify-between gap-4 py-3.5 first:pt-1"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-bold text-[var(--ink)]">
                        {isWeight
                          ? WEIGHT_CATEGORY_NAME
                          : (category?.name ??
                            'Показатель')}
                      </p>
                      <p className="mt-0.5 text-xs text-[var(--ink)]/50">
                        {formatDateTime(state.time)}
                      </p>
                    </div>
                    <p className="shrink-0 text-lg font-black text-[var(--forest)]">
                      {isWeight ? (
                        formatWeight(state.value)
                      ) : (
                        <>
                          {numberFormatter.format(
                            state.value,
                          )}{' '}
                          <span className="text-xs font-bold">
                            {category
                              ? unitLabels[category.unit]
                              : ''}
                          </span>
                        </>
                      )}
                    </p>
                  </li>
                );
              })}
            </ol>
          ) : (
            <EmptyLine>Измерений пока нет.</EmptyLine>
          )}
        </article>

        <article className="border-t border-[var(--forest)]/15 p-5 sm:p-7 xl:border-t-0">
          <h2 className="text-xl font-black text-[var(--forest)]">
            Последнее кормление
          </h2>
          {foods.isPending ? (
            <EmptyLine>Загружаем запись…</EmptyLine>
          ) : latestFood ? (
            <div className="mt-4 bg-[var(--cream)] p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-2xl font-black text-[var(--forest)]">
                    {latestFood.name}
                  </p>
                  <p className="mt-1 text-xs text-[var(--ink)]/50">
                    {formatDateTime(latestFood.createdAt)}
                  </p>
                </div>
                {latestFood.weight ? (
                  <b className="shrink-0 text-lg text-[var(--forest)]">
                    {latestFood.weight} г
                  </b>
                ) : null}
              </div>
              {latestFood.ingredients?.length ? (
                <p className="mt-5 text-sm leading-6 text-[var(--ink)]/65">
                  Состав:{' '}
                  {latestFood.ingredients.join(', ')}
                </p>
              ) : null}
              <div className="mt-5 flex flex-wrap gap-2">
                {latestFood.isApproach !== null ? (
                  <span className="border border-[var(--forest)]/20 bg-white px-2 py-1 text-xs font-bold text-[var(--forest)]">
                    {latestFood.isApproach
                      ? 'Понравился'
                      : 'Не понравился'}
                  </span>
                ) : null}
                {latestFood.isTolerability !== null ? (
                  <span className="border border-[var(--forest)]/20 bg-white px-2 py-1 text-xs font-bold text-[var(--forest)]">
                    {latestFood.isTolerability
                      ? 'Подошёл'
                      : 'Не подошёл'}
                  </span>
                ) : null}
              </div>
            </div>
          ) : (
            <EmptyLine>
              Кормления пока не записаны.
            </EmptyLine>
          )}
        </article>
      </section>
    </div>
  );
}
