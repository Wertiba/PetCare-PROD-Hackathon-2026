'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import type { State } from '@src/entities/state';
import { Uid } from '@src/shared/api/global.types';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useForm } from 'react-hook-form';

import { useCreateStateMutation } from '../model/create-state.mutation';
import {
  type AddWeightValues,
  addWeightSchema,
  toNumber,
  todayInputValue,
} from '../model/validation';

const checkedChipClassName =
  'inline-flex cursor-pointer items-center rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-semibold text-[var(--ink)]/75 transition-colors hover:border-[var(--forest)] hover:text-[var(--forest)] peer-checked:border-[var(--forest)] peer-checked:bg-[var(--lime)] peer-checked:text-[var(--forest)] peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[var(--forest)]';

const units: {
  value: AddWeightValues['unit'];
  label: string;
}[] = [
  { value: 'kg', label: 'кг' },
  { value: 'g', label: 'г' },
];

interface AddWeightFormProps {
  petId: Uid;
  catId: Uid;
  onSuccess?: (state: State) => void;
}

export function AddWeightForm({
  petId,
  catId,
  onSuccess,
}: AddWeightFormProps) {
  const { mutate, isPending, error } =
    useCreateStateMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AddWeightValues>({
    defaultValues: {
      value: '',
      unit: 'kg',
      date: todayInputValue(),
    },
    mode: 'onTouched',
    resolver: zodResolver(addWeightSchema),
  });

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) =>
          mutate(
            {
              petId,
              categoryId: catId,
              // The «Вес» category stores whole grams.
              value: Math.round(
                toNumber(values.value) *
                  (values.unit === 'kg' ? 1000 : 1),
              ),
              time:
                values.date === todayInputValue()
                  ? Date.now() / 1000
                  : new Date(
                      `${values.date}T00:00`,
                    ).getTime() / 1000,
            },
            { onSuccess },
          ),
        )(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
        <FormField
          id="weight-value"
          label="Вес"
          type="text"
          inputMode="decimal"
          placeholder="Например, 4,2"
          autoComplete="off"
          error={errors.value?.message}
          {...register('value')}
        />
        <fieldset className="pt-7">
          <legend className="sr-only">Единицы</legend>
          <div className="flex gap-1">
            {units.map((unit) => (
              <label key={unit.value}>
                <input
                  type="radio"
                  value={unit.value}
                  className="peer sr-only"
                  {...register('unit')}
                />
                <span
                  className={`${checkedChipClassName} py-3`}
                >
                  {unit.label}
                </span>
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <FormField
        id="weight-date"
        label="Дата взвешивания"
        type="date"
        error={errors.date?.message}
        {...register('date')}
      />

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить вес. Попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Сохранить вес
      </SubmitButton>
    </form>
  );
}
