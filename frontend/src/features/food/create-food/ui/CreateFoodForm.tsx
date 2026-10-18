'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import type { Food } from '@src/entities/food';
import { Uid } from '@src/shared/api/global.types';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useState } from 'react';
import { useForm, useWatch } from 'react-hook-form';

import { useCreateFoodMutation } from '../model/create-food.mutation';
import {
  portionTemplates,
  reactionTemplates,
} from '../model/templates';
import {
  type CreateFoodValues,
  createFoodSchema,
} from '../model/validation';

const chipClassName =
  'inline-flex cursor-pointer items-center rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-semibold text-[var(--ink)]/75 transition-colors hover:border-[var(--forest)] hover:text-[var(--forest)]';
const checkedChipClassName = `${chipClassName} peer-checked:border-[var(--forest)] peer-checked:bg-[var(--lime)] peer-checked:text-[var(--forest)] peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[var(--forest)]`;
const pressedChipClassName = `${chipClassName} aria-pressed:border-[var(--forest)] aria-pressed:bg-[var(--lime)] aria-pressed:text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]`;
const legendClassName =
  'mb-2 text-sm font-semibold tracking-[0.01em] text-[var(--forest)]';
const inputClassName =
  'w-full rounded-sm border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]';

const INITIAL_VALUES: CreateFoodValues = {
  name: '',
  weight: '',
  isApproach: null,
  isTolerability: null,
  reactions: [],
  details: '',
  ingredients: '',
};

const assessments: {
  name: 'isApproach' | 'isTolerability';
  legend: string;
  options: {
    value: Exclude<CreateFoodValues['isApproach'], null>;
    label: string;
  }[];
}[] = [
  {
    name: 'isApproach',
    legend: 'Понравился?',
    options: [
      { value: 'yes', label: 'Ел с аппетитом' },
      { value: 'no', label: 'Не понравился' },
      { value: 'unknown', label: 'Непонятно' },
    ],
  },
  {
    name: 'isTolerability',
    legend: 'Подошёл?',
    options: [
      { value: 'yes', label: 'Всё хорошо' },
      { value: 'no', label: 'Не подошёл' },
      { value: 'unknown', label: 'Пока не ясно' },
    ],
  },
];

const toAssessment = (
  value: CreateFoodValues['isApproach'],
) => (value === 'unknown' ? null : value === 'yes');

interface CreateFoodFormProps {
  petId: Uid;
  recentNames?: string[];
  onSuccess?: (food: Food) => void;
}

export function CreateFoodForm({
  petId,
  recentNames = [],
  onSuccess,
}: CreateFoodFormProps) {
  const [formVersion, setFormVersion] = useState(0);
  const { mutate, isPending, error } =
    useCreateFoodMutation();
  const {
    register,
    control,
    setValue,
    setFocus,
    reset,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateFoodValues>({
    defaultValues: INITIAL_VALUES,
    mode: 'onTouched',
    resolver: zodResolver(createFoodSchema),
  });

  const [name, weight] = useWatch({
    control,
    name: ['name', 'weight'],
  });

  return (
    <form
      key={formVersion}
      onSubmit={(event) => {
        void handleSubmit((values) => {
          const consequences = [
            values.reactions.join(', '),
            values.details.trim(),
          ]
            .filter(Boolean)
            .join('. ');

          mutate(
            {
              petId,
              name: values.name,
              weight: values.weight
                ? Number(values.weight)
                : null,
              ingredients: values.ingredients
                .split(',')
                .map((item) => item.trim())
                .filter(Boolean),
              isApproach: toAssessment(values.isApproach),
              isTolerability: toAssessment(
                values.isTolerability,
              ),
              consequences: consequences || null,
            },
            {
              onSuccess: (food) => {
                reset(INITIAL_VALUES);
                setFormVersion((version) => version + 1);
                onSuccess?.(food);
              },
            },
          );
        })(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <div className="flex flex-col gap-3">
        <FormField
          id="food-name"
          label="Корм"
          type="text"
          placeholder="Название корма или продукта"
          autoComplete="off"
          error={errors.name?.message}
          {...register('name')}
        />
        {recentNames.length ? (
          <div
            className="flex flex-wrap gap-2"
            aria-label="Недавние корма"
            role="group"
          >
            {recentNames.map((recentName) => (
              <button
                key={recentName}
                type="button"
                aria-pressed={name === recentName}
                onClick={() =>
                  setValue('name', recentName, {
                    shouldValidate: true,
                  })
                }
                className={pressedChipClassName}
              >
                {recentName}
              </button>
            ))}
            <button
              type="button"
              aria-pressed={
                name.trim() !== '' &&
                !recentNames.includes(name)
              }
              onClick={() => {
                if (recentNames.includes(name)) {
                  setValue('name', '');
                }
                setFocus('name');
              }}
              className={pressedChipClassName}
            >
              Свой вариант
            </button>
          </div>
        ) : null}
      </div>

      <fieldset>
        <legend className={legendClassName}>
          Порция, г{' '}
          <span className="font-normal text-[var(--ink)]/50">
            — необязательно
          </span>
        </legend>
        <div className="flex flex-wrap items-center gap-2">
          {portionTemplates.map((portion) => (
            <button
              key={portion}
              type="button"
              aria-pressed={weight === String(portion)}
              onClick={() =>
                setValue('weight', String(portion), {
                  shouldValidate: true,
                })
              }
              className={pressedChipClassName}
            >
              {portion}
            </button>
          ))}
          <input
            type="text"
            inputMode="numeric"
            placeholder="Своя"
            aria-label="Своя порция в граммах"
            aria-invalid={errors.weight ? true : undefined}
            className="w-24 rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:border-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
            {...register('weight')}
          />
        </div>
        {errors.weight ? (
          <span
            role="alert"
            className="mt-2 block text-sm text-red-700"
          >
            {errors.weight.message}
          </span>
        ) : null}
      </fieldset>

      <div className="grid gap-5 sm:grid-cols-2">
        {assessments.map((assessment) => (
          <fieldset key={assessment.name}>
            <legend className={legendClassName}>
              {assessment.legend}
            </legend>
            <div className="flex flex-wrap gap-2">
              {assessment.options.map((option) => (
                <label key={option.value}>
                  <input
                    type="radio"
                    value={option.value}
                    className="peer sr-only"
                    {...register(assessment.name)}
                  />
                  <span className={checkedChipClassName}>
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
        ))}
      </div>

      <fieldset>
        <legend className={legendClassName}>
          Реакции{' '}
          <span className="font-normal text-[var(--ink)]/50">
            — если были
          </span>
        </legend>
        <div className="flex flex-wrap gap-2">
          {reactionTemplates.map((reaction) => (
            <label key={reaction}>
              <input
                type="checkbox"
                value={reaction}
                className="peer sr-only"
                {...register('reactions')}
              />
              <span className={checkedChipClassName}>
                {reaction}
              </span>
            </label>
          ))}
        </div>
        <textarea
          rows={2}
          aria-label="Подробнее о реакции"
          placeholder="Подробнее: когда началось, как проявлялось"
          aria-invalid={errors.details ? true : undefined}
          className={`${inputClassName} mt-3 resize-y`}
          {...register('details')}
        />
        {errors.details ? (
          <span
            role="alert"
            className="mt-2 block text-sm text-red-700"
          >
            {errors.details.message}
          </span>
        ) : null}
      </fieldset>

      <details
        open={errors.ingredients ? true : undefined}
        className="group rounded-sm border border-[var(--forest)]/20 bg-white px-4 py-3"
      >
        <summary className="cursor-pointer text-sm font-semibold text-[var(--forest)] marker:text-[var(--forest)]/50">
          Состав корма
        </summary>
        <div className="mt-3">
          <FormField
            id="food-ingredients"
            label="Ингредиенты через запятую"
            type="text"
            placeholder="Курица, рис, морковь"
            autoComplete="off"
            error={errors.ingredients?.message}
            {...register('ingredients')}
          />
        </div>
      </details>

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить кормление. Попробуйте ещё
          раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Записать кормление
      </SubmitButton>
    </form>
  );
}
