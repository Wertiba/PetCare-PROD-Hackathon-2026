'use client';

import type { Food } from '@src/entities/food';
import { reactionTemplates } from '@src/features/food/create-food';
import { useMemo } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const PERIOD_DAYS = 14;
const DAY_MS = 24 * 60 * 60 * 1000;
const OTHER_REACTION = 'Иное';

const POSITIVE_COLOR = 'var(--forest)';
const NEGATIVE_COLOR = 'var(--color-red-700)';

const dayFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
});
const gramsFormatter = new Intl.NumberFormat('ru-RU', {
  maximumFractionDigits: 0,
});
const formatGrams = (value: number) =>
  `${gramsFormatter.format(value)} г`;

const axisTick = {
  fill: 'var(--ink)',
  fillOpacity: 0.6,
  fontSize: 12,
};
const tooltipProps = {
  contentStyle: {
    background: 'var(--white)',
    border: '1px solid var(--forest)',
    borderRadius: 2,
    color: 'var(--ink)',
    fontSize: 13,
  },
  labelStyle: { color: 'var(--ink)', fontWeight: 700 },
  itemStyle: { color: 'var(--ink)' },
};

const startOfDay = (date: Date) =>
  new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
  ).getTime();

interface DailyIntake {
  day: number;
  label: string;
  grams: number;
}

interface AssessmentCount {
  label: string;
  count: number;
  positive: boolean;
}

function StatTile({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-sm border border-[var(--forest)]/15 bg-white px-3 py-2">
      <dt className="text-xs text-[var(--ink)]/55">
        {label}
      </dt>
      <dd className="mt-0.5 text-lg font-black text-[var(--forest)]">
        {value}
      </dd>
    </div>
  );
}

export function FoodStats({ items }: { items: Food[] }) {
  const intake = useMemo(() => {
    const today = startOfDay(new Date());
    const dayGrams = new Map<number, number>();

    let portions = 0;
    let portionsGrams = 0;
    for (const food of items) {
      if (!food.weight) continue;
      const day = startOfDay(
        new Date(food.createdAt * 1000),
      );
      if (
        day < today - (PERIOD_DAYS - 1) * DAY_MS ||
        day > today
      ) {
        continue;
      }
      dayGrams.set(
        day,
        (dayGrams.get(day) ?? 0) + food.weight,
      );
      portions += 1;
      portionsGrams += food.weight;
    }

    const days: DailyIntake[] = Array.from(
      { length: PERIOD_DAYS },
      (_, index) => {
        const day =
          today - (PERIOD_DAYS - 1 - index) * DAY_MS;
        return {
          day,
          label: dayFormatter.format(day),
          grams: dayGrams.get(day) ?? 0,
        };
      },
    );

    return {
      days,
      total: portionsGrams,
      averagePerDay: portionsGrams / PERIOD_DAYS,
      averagePortion: portions
        ? portionsGrams / portions
        : 0,
    };
  }, [items]);

  const assessments = useMemo(() => {
    const count = (predicate: (food: Food) => boolean) =>
      items.filter(predicate).length;

    const reactions = new Map<string, number>();
    for (const food of items) {
      if (!food.consequences) continue;
      const matched = reactionTemplates.filter((reaction) =>
        food.consequences?.includes(reaction),
      );
      for (const reaction of matched.length
        ? matched
        : [OTHER_REACTION]) {
        reactions.set(
          reaction,
          (reactions.get(reaction) ?? 0) + 1,
        );
      }
    }

    const result: AssessmentCount[] = [
      {
        label: 'Понравился',
        count: count((food) => food.isApproach === true),
        positive: true,
      },
      {
        label: 'Подошёл',
        count: count(
          (food) => food.isTolerability === true,
        ),
        positive: true,
      },
      {
        label: 'Не понравился',
        count: count((food) => food.isApproach === false),
        positive: false,
      },
      {
        label: 'Не подошёл',
        count: count(
          (food) => food.isTolerability === false,
        ),
        positive: false,
      },
      ...[...reactions]
        .sort((a, b) => b[1] - a[1])
        .map(([label, value]) => ({
          label,
          count: value,
          positive: false,
        })),
    ];
    return result.filter((item) => item.count > 0);
  }, [items]);

  return (
    <section
      aria-labelledby="food-stats-title"
      className="rounded-md border border-[var(--forest)]/25 bg-[var(--cream)] p-5"
    >
      <h2
        id="food-stats-title"
        className="text-xl font-black text-[var(--forest)]"
      >
        Статистика питания
      </h2>
      <p className="mt-1 text-sm text-[var(--ink)]/60">
        Потребление корма за последние {PERIOD_DAYS} дней
      </p>

      <dl className="mt-4 grid gap-2 sm:grid-cols-3">
        <StatTile
          label="Всего за период"
          value={formatGrams(intake.total)}
        />
        <StatTile
          label="В среднем за день"
          value={formatGrams(intake.averagePerDay)}
        />
        <StatTile
          label="Средняя порция"
          value={
            intake.averagePortion
              ? formatGrams(intake.averagePortion)
              : '—'
          }
        />
      </dl>

      {intake.total ? (
        <div
          role="img"
          aria-label={`Съедено за ${PERIOD_DAYS} дней: ${formatGrams(intake.total)}, в среднем ${formatGrams(intake.averagePerDay)} в день`}
          className="mt-4 h-56"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={intake.days}
              margin={{
                top: 16,
                right: 8,
                bottom: 0,
                left: -8,
              }}
            >
              <defs>
                <linearGradient
                  id="food-intake-fill"
                  x1="0"
                  x2="0"
                  y1="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor={POSITIVE_COLOR}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="100%"
                    stopColor={POSITIVE_COLOR}
                    stopOpacity={0.02}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid
                vertical={false}
                stroke="var(--forest)"
                strokeOpacity={0.12}
              />
              <XAxis
                dataKey="label"
                tick={axisTick}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
                minTickGap={16}
              />
              <YAxis
                tick={axisTick}
                tickLine={false}
                axisLine={false}
                allowDecimals={false}
                width={48}
              />
              <Tooltip
                {...tooltipProps}
                cursor={{
                  stroke: 'var(--forest)',
                  strokeOpacity: 0.3,
                }}
                formatter={(value) => [
                  formatGrams(Number(value)),
                  'Съедено',
                ]}
              />
              <ReferenceLine
                y={intake.averagePerDay}
                stroke="var(--forest)"
                strokeDasharray="4 4"
                strokeOpacity={0.6}
                label={{
                  value: `среднее ${formatGrams(intake.averagePerDay)}`,
                  position: 'insideTopRight',
                  fill: 'var(--ink)',
                  fillOpacity: 0.7,
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="grams"
                stroke={POSITIVE_COLOR}
                strokeWidth={2}
                fill="url(#food-intake-fill)"
                activeDot={{ r: 4 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="py-4 text-sm text-[var(--ink)]/60">
          Указывайте вес порции — тогда здесь появится
          график потребления.
        </p>
      )}

      <h3 className="mt-6 text-sm font-semibold text-[var(--forest)]">
        Оценки и реакции
      </h3>
      {assessments.length ? (
        <div
          role="img"
          aria-label={assessments
            .map((item) => `${item.label}: ${item.count}`)
            .join(', ')}
          className="mt-2"
        >
          <ResponsiveContainer
            width="100%"
            height={assessments.length * 32 + 16}
          >
            <BarChart
              data={assessments}
              layout="vertical"
              barCategoryGap={6}
              margin={{
                top: 0,
                right: 32,
                bottom: 0,
                left: 0,
              }}
            >
              <XAxis
                type="number"
                hide
                allowDecimals={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                tick={axisTick}
                tickLine={false}
                axisLine={false}
                width={128}
              />
              <Tooltip
                {...tooltipProps}
                cursor={{
                  fill: 'var(--forest)',
                  fillOpacity: 0.06,
                }}
                formatter={(value) => [value, 'Кормлений']}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {assessments.map((item) => (
                  <Cell
                    key={item.label}
                    fill={
                      item.positive
                        ? POSITIVE_COLOR
                        : NEGATIVE_COLOR
                    }
                  />
                ))}
                <LabelList
                  dataKey="count"
                  position="right"
                  fill="var(--ink)"
                  fontSize={12}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="py-4 text-sm text-[var(--ink)]/60">
          Пока нет оценок кормов.
        </p>
      )}
    </section>
  );
}
