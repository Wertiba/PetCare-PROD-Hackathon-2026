'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';

import { useCreateEventMutation } from '../model/create-event.mutation';
import {
  type CreateEventValues,
  createEventSchema,
} from '../model/validation';

const PERIOD_LABELS: Record<
  CreateEventValues['period'],
  string
> = {
  none: 'Не повторять',
  daily: 'Каждый день',
  weekly: 'Каждую неделю',
  monthly: 'Каждый месяц',
  quarterly: 'Каждый квартал',
  half_year: 'Каждые полгода',
  yearly: 'Каждый год',
};

export function CreateEventForm() {
  const petId = useSearchParams().get('petId') ?? '';
  const { mutate, isPending, error } =
    useCreateEventMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateEventValues>({
    defaultValues: {
      petId,
      name: '',
      schedule: '',
      period: 'none',
    },
    mode: 'onTouched',
    resolver: zodResolver(createEventSchema),
  });

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) =>
          mutate({
            petId: values.petId,
            name: values.name,
            type: 'other',
            status: 'planned',
            schedule:
              new Date(values.schedule).getTime() / 1000,
            period: values.period,
          }),
        )(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <FormField
        label="Название"
        type="text"
        placeholder="Введите название события"
        error={errors.name?.message}
        {...register('name')}
      />

      <FormField
        label="Дата и время"
        type="datetime-local"
        error={errors.schedule?.message}
        {...register('schedule')}
      />

      <div className="flex flex-col gap-2">
        <label
          htmlFor="period"
          className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
        >
          Повторение
        </label>
        <select
          id="period"
          className="w-full border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
          {...register('period')}
        >
          {Object.entries(PERIOD_LABELS).map(
            ([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ),
          )}
        </select>
      </div>

      {errors.petId ? (
        <p role="alert" className="text-sm text-red-700">
          Не указан питомец (параметр petId в адресе).
        </p>
      ) : null}

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось добавить событие. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Добавить событие
      </SubmitButton>
    </form>
  );
}
