'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import {
  type Event,
  type EventPeriod,
  type EventType,
  eventPeriodLabels,
} from '@src/entities/event';
import { Uid } from '@src/shared/api/global.types';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useForm, useWatch } from 'react-hook-form';

import { useCreateEventMutation } from '../model/create-event.mutation';
import { eventNameTemplates } from '../model/templates';
import {
  type CreateHealthEventValues,
  createHealthEventSchema,
} from '../model/validation';

const chipClassName =
  'inline-flex cursor-pointer items-center rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-semibold text-[var(--ink)]/75 transition-colors hover:border-[var(--forest)] hover:text-[var(--forest)]';
const checkedChipClassName = `${chipClassName} peer-checked:border-[var(--forest)] peer-checked:bg-[var(--lime)] peer-checked:text-[var(--forest)] peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[var(--forest)]`;
const pressedChipClassName = `${chipClassName} aria-pressed:border-[var(--forest)] aria-pressed:bg-[var(--lime)] aria-pressed:text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]`;
const legendClassName =
  'mb-2 text-sm font-semibold tracking-[0.01em] text-[var(--forest)]';

const periods = Object.keys(
  eventPeriodLabels,
) as EventPeriod[];

const descriptionLabels: Partial<
  Record<EventType, { label: string; placeholder: string }>
> = {
  vet_visit: {
    label: 'Заключение врача',
    placeholder: 'Диагноз, рекомендации, назначения',
  },
  medication: {
    label: 'Схема приёма',
    placeholder: 'Дозировка, сколько дней, как давать',
  },
};

const dateFromToday = (days: number) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 10);
};

const quickDates: Record<
  CreateHealthEventValues['status'],
  { label: string; days: number }[]
> = {
  done: [
    { label: 'Сегодня', days: 0 },
    { label: 'Вчера', days: -1 },
  ],
  planned: [
    { label: 'Сегодня', days: 0 },
    { label: 'Завтра', days: 1 },
    { label: 'Через неделю', days: 7 },
    { label: 'Через месяц', days: 30 },
  ],
};

interface CreateHealthEventFormProps {
  petId: Uid;
  type: EventType;
  onSuccess?: (event: Event) => void;
}

export function CreateHealthEventForm({
  petId,
  type,
  onSuccess,
}: CreateHealthEventFormProps) {
  const { mutate, isPending, error } =
    useCreateEventMutation();
  const {
    register,
    control,
    setValue,
    setFocus,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateHealthEventValues>({
    defaultValues: {
      name: '',
      status: 'done',
      date: dateFromToday(0),
      period: 'none',
      description: '',
    },
    mode: 'onTouched',
    resolver: zodResolver(createHealthEventSchema),
  });

  const [name, status, date] = useWatch({
    control,
    name: ['name', 'status', 'date'],
  });
  const statusField = register('status', {
    onChange: (
      event: React.ChangeEvent<HTMLInputElement>,
    ) =>
      setValue(
        'date',
        dateFromToday(
          event.target.value === 'planned' ? 1 : 0,
        ),
      ),
  });
  const templates = eventNameTemplates[type];
  const description = descriptionLabels[type] ?? {
    label: 'Заметка',
    placeholder: 'Препарат, клиника, самочувствие',
  };

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) =>
          mutate(
            {
              petId,
              type,
              name: values.name,
              status: values.status,
              // Local midnight, so the day doesn't shift for users west of UTC
              schedule:
                new Date(`${values.date}T00:00`).getTime() /
                1000,
              period: values.period,
              ...(values.description.trim()
                ? { description: values.description.trim() }
                : {}),
            },
            { onSuccess },
          ),
        )(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <div className="flex flex-col gap-3">
        <FormField
          id="health-event-name"
          label="Название"
          type="text"
          placeholder={
            templates.length
              ? 'Выберите ниже или введите своё'
              : 'Что произошло'
          }
          error={errors.name?.message}
          {...register('name')}
        />
        {templates.length ? (
          <div
            className="flex flex-wrap gap-2"
            aria-label="Частые варианты"
            role="group"
          >
            {templates.map((template) => (
              <button
                key={template}
                type="button"
                aria-pressed={name === template}
                onClick={() =>
                  setValue('name', template, {
                    shouldValidate: true,
                  })
                }
                className={pressedChipClassName}
              >
                {template}
              </button>
            ))}
            <button
              type="button"
              aria-pressed={
                name.trim() !== '' &&
                !templates.includes(name)
              }
              onClick={() => {
                if (templates.includes(name)) {
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
        <legend className={legendClassName}>Когда</legend>
        <div className="flex flex-wrap gap-2">
          <label>
            <input
              type="radio"
              value="done"
              className="peer sr-only"
              {...statusField}
            />
            <span className={checkedChipClassName}>
              Уже было
            </span>
          </label>
          <label>
            <input
              type="radio"
              value="planned"
              className="peer sr-only"
              {...statusField}
            />
            <span className={checkedChipClassName}>
              Запланировать
            </span>
          </label>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {quickDates[status].map((item) => (
            <button
              key={item.label}
              type="button"
              aria-pressed={
                date === dateFromToday(item.days)
              }
              onClick={() =>
                setValue('date', dateFromToday(item.days), {
                  shouldValidate: true,
                })
              }
              className={pressedChipClassName}
            >
              {item.label}
            </button>
          ))}
          <input
            type="date"
            aria-label="Дата"
            aria-invalid={errors.date ? true : undefined}
            className="rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm text-[var(--ink)] focus:border-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
            {...register('date')}
          />
        </div>
        {errors.date ? (
          <span
            role="alert"
            className="mt-2 block text-sm text-red-700"
          >
            {errors.date.message}
          </span>
        ) : null}
      </fieldset>

      <fieldset>
        <legend className={legendClassName}>
          Повторять
        </legend>
        <div className="flex flex-wrap gap-2">
          {periods.map((period) => (
            <label key={period}>
              <input
                type="radio"
                value={period}
                className="peer sr-only"
                {...register('period')}
              />
              <span className={checkedChipClassName}>
                {eventPeriodLabels[period]}
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="health-event-description"
          className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
        >
          {description.label}{' '}
          <span className="font-normal text-[var(--ink)]/50">
            — необязательно
          </span>
        </label>
        <textarea
          id="health-event-description"
          rows={3}
          placeholder={description.placeholder}
          aria-invalid={
            errors.description ? true : undefined
          }
          className="w-full resize-y rounded-sm border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
          {...register('description')}
        />
        {errors.description ? (
          <span
            role="alert"
            className="text-sm text-red-700"
          >
            {errors.description.message}
          </span>
        ) : null}
      </div>

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить запись. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Сохранить запись
      </SubmitButton>
    </form>
  );
}
