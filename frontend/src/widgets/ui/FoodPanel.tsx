'use client';

import {
  type Food,
  useGetFoodsQuery,
} from '@src/entities/food';
import type { Pet } from '@src/entities/pet';
import { CreateFoodForm } from '@src/features/food/create-food';
import { useMemo, useState } from 'react';

const RECENT_NAMES_LIMIT = 6;

interface FoodVerdict {
  name: string;
  count: number;
  liked: boolean | null;
  suitable: boolean | null;
  reactions: string[];
}

const dateTimeFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
});

const pluralRules = new Intl.PluralRules('ru-RU');
const formatFeedings = (count: number) => {
  const rule = pluralRules.select(count);
  return `${count} ${
    rule === 'one'
      ? 'кормление'
      : rule === 'few'
        ? 'кормления'
        : 'кормлений'
  }`;
};

const badgeClassName =
  'inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-semibold';
const positiveBadgeClassName = `${badgeClassName} border-[var(--forest)]/30 bg-[var(--lime)] text-[var(--forest)]`;
const negativeBadgeClassName = `${badgeClassName} border-red-800/40 bg-red-50 text-red-800`;
const neutralBadgeClassName = `${badgeClassName} border-[var(--ink)]/20 text-[var(--ink)]/65`;

function FoodItem({ food }: { food: Food }) {
  const createdAt = new Date(food.createdAt * 1000);

  return (
    <li className="border-b border-[var(--forest)]/10 py-4 last:border-b-0">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <p className="min-w-0 font-bold break-words text-[var(--ink)]">
          {food.name}
          {food.weight ? (
            <span className="font-normal text-[var(--ink)]/55">
              {' '}
              · {food.weight} г
            </span>
          ) : null}
        </p>
        <time
          dateTime={createdAt.toISOString()}
          className="shrink-0 text-sm text-[var(--ink)]/55"
        >
          {dateTimeFormatter.format(createdAt)}
        </time>
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5 empty:hidden">
        {food.isApproach === null ? null : (
          <span
            className={
              food.isApproach
                ? positiveBadgeClassName
                : neutralBadgeClassName
            }
          >
            {food.isApproach
              ? 'Понравился'
              : 'Не понравился'}
          </span>
        )}
        {food.isTolerability === null ? null : (
          <span
            className={
              food.isTolerability
                ? positiveBadgeClassName
                : negativeBadgeClassName
            }
          >
            {food.isTolerability ? 'Подошёл' : 'Не подошёл'}
          </span>
        )}
      </div>
      {food.consequences ? (
        <p className="mt-2 border-l-2 border-red-700/50 pl-3 text-sm leading-6 break-words text-[var(--ink)]/75">
          {food.consequences}
        </p>
      ) : null}
      {food.ingredients?.length ? (
        <p className="mt-2 text-xs leading-5 text-[var(--ink)]/55">
          Состав: {food.ingredients.join(', ')}
        </p>
      ) : null}
    </li>
  );
}

function VerdictList({
  items,
  title,
}: {
  items: FoodVerdict[];
  title: string;
}) {
  if (!items.length) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold text-[var(--forest)]">
        {title}
      </h3>
      <ul className="mt-2 space-y-2">
        {items.map((item) => (
          <li
            key={item.name}
            className="rounded-sm border border-[var(--forest)]/15 bg-white px-3 py-2"
          >
            <p className="font-bold break-words text-[var(--ink)]">
              {item.name}
            </p>
            <p className="text-xs text-[var(--ink)]/55">
              {formatFeedings(item.count)}
              {item.liked === null
                ? ''
                : item.liked
                  ? ' · нравится'
                  : ' · не нравится'}
            </p>
            {item.reactions.length ? (
              <p className="mt-1 text-xs leading-5 break-words text-red-800">
                {item.reactions.join('; ')}
              </p>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function FoodPanel({
  pet,
  onOpenReminders,
}: {
  pet: Pet;
  onOpenReminders: () => void;
}) {
  const [saved, setSaved] = useState<string | null>(null);
  const foods = useGetFoodsQuery({
    page: 0,
    size: 100,
    petId: pet.id,
  });

  const items = foods.data?.items;
  const verdicts = useMemo(() => {
    // Foods come newest first, so the first assessment found per name is the latest one.
    const byName = new Map<string, FoodVerdict>();
    for (const food of items ?? []) {
      const key = food.name.trim().toLowerCase();
      const verdict = byName.get(key) ?? {
        name: food.name.trim(),
        count: 0,
        liked: null,
        suitable: null,
        reactions: [],
      };
      verdict.count += 1;
      verdict.liked ??= food.isApproach;
      verdict.suitable ??= food.isTolerability;
      if (food.consequences) {
        verdict.reactions.push(food.consequences);
      }
      byName.set(key, verdict);
    }
    return [...byName.values()];
  }, [items]);

  const recentNames = verdicts
    .slice(0, RECENT_NAMES_LIMIT)
    .map((item) => item.name);
  const suitable = verdicts.filter(
    (item) => item.suitable === true,
  );
  const unsuitable = verdicts.filter(
    (item) => item.suitable === false,
  );
  const unknown = verdicts.filter(
    (item) => item.suitable === null,
  );

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_.8fr] xl:items-start">
      <div className="grid content-start gap-5">
        <section
          aria-labelledby="food-history-title"
          className="rounded-md border-2 border-[var(--forest)] bg-white p-5 shadow-[4px_4px_0_var(--lime)]"
        >
          <h2
            id="food-history-title"
            className="text-xl font-black text-[var(--forest)]"
          >
            Дневник питания
          </h2>
          <p className="mt-1 text-sm text-[var(--ink)]/60">
            Корма, порции и реакции на них
          </p>

          {foods.isPending ? (
            <p className="py-6 text-sm text-[var(--ink)]/60">
              Загружаем дневник…
            </p>
          ) : foods.isError ? (
            <p
              role="alert"
              className="mt-5 border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
            >
              Не удалось загрузить дневник. Обновите
              страницу.
            </p>
          ) : items?.length ? (
            <ol className="mt-3">
              {items.map((food) => (
                <FoodItem key={food.id} food={food} />
              ))}
            </ol>
          ) : (
            <p className="py-6 text-sm text-[var(--ink)]/60">
              Пока нет записей. Запишите первое кормление —
              так со временем станет видно, какие корма
              подходят.
            </p>
          )}
          <button
            type="button"
            onClick={onOpenReminders}
            className="mt-4 text-sm font-bold text-[var(--forest)] underline underline-offset-2 hover:text-[var(--forest)]/75 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
          >
            Напомнить покормить →
          </button>
        </section>

        {verdicts.length ? (
          <section
            aria-labelledby="food-profile-title"
            className="rounded-md border border-[var(--forest)]/25 bg-[var(--cream)] p-5"
          >
            <h2
              id="food-profile-title"
              className="text-xl font-black text-[var(--forest)]"
            >
              Профиль питания
            </h2>
            <p className="mt-1 text-sm text-[var(--ink)]/60">
              {pet.name}: последняя оценка каждого корма
            </p>
            <div className="mt-4 space-y-5">
              <VerdictList
                title="Не подходит"
                items={unsuitable}
              />
              <VerdictList
                title="Подходит"
                items={suitable}
              />
              <VerdictList
                title="Пока не ясно"
                items={unknown}
              />
            </div>
          </section>
        ) : null}
      </div>

      <div>
        <section
          aria-labelledby="food-entry-title"
          className="rounded-md border border-[var(--forest)]/25 bg-white p-5"
        >
          <h2
            id="food-entry-title"
            className="text-xl font-black text-[var(--forest)]"
          >
            Записать кормление
          </h2>
          <p className="mt-1 mb-5 text-sm text-[var(--ink)]/60">
            Нравится и подходит — разные вопросы: корм может
            нравиться, но не подходить.
          </p>
          {saved ? (
            <p
              role="status"
              className="mb-5 border-l-4 border-[var(--forest)] bg-[var(--lime)]/40 px-4 py-3 text-sm font-semibold text-[var(--forest)]"
            >
              {saved} — сохранено в дневнике
            </p>
          ) : null}
          <CreateFoodForm
            petId={pet.id}
            recentNames={recentNames}
            onSuccess={(food) => setSaved(food.name)}
          />
        </section>
      </div>
    </div>
  );
}
