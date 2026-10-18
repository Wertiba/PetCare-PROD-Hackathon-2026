'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import type { Notification } from '@src/entities/notification';
import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';
import { ensureWebPushPermission } from '@src/shared/lib/web-push';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useState } from 'react';
import { useForm } from 'react-hook-form';

import { useCreateNotificationMutation } from '../model/create-notification.mutation';
import {
  type CreateNotificationValues,
  createNotificationSchema,
} from '../model/validation';

const TYPE_LABELS: Record<
  CreateNotificationValues['type'],
  string
> = {
  app: 'В приложении (скоро)',
  telegram: 'Telegram (скоро)',
  web_push: 'Push в браузере',
};

const todayInputValue = () => {
  const date = new Date();
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 10);
};

const toDateTimeInputValue = (timestamp: Timestamp) => {
  const date = new Date(timestamp * 1000);
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 16);
};

interface CreateNotificationFormProps {
  eventId: Uid;
  defaultTime?: Timestamp;
  onCancel?: () => void;
  onSuccess?: (notification: Notification) => void;
}

export function CreateNotificationForm({
  eventId,
  defaultTime,
  onCancel,
  onSuccess,
}: CreateNotificationFormProps) {
  const { mutate, isPending, error } =
    useCreateNotificationMutation();
  const [permissionError, setPermissionError] = useState<
    string | null
  >(null);
  const today = todayInputValue();
  const initialClock = defaultTime
    ? toDateTimeInputValue(defaultTime).slice(11)
    : '';
  const initialValues: CreateNotificationValues = {
    type: 'web_push',
    time: initialClock ? `${today}T${initialClock}` : '',
  };
  const {
    register,
    reset,
    setValue,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateNotificationValues>({
    defaultValues: initialValues,
    mode: 'onTouched',
    resolver: zodResolver(createNotificationSchema),
  });

  // Parts live in local state: a half-filled value ("2026-10-20T") is not a valid datetime.
  const [datePart, setDatePart] = useState(today);
  const [timePart, setTimePart] = useState(initialClock);

  const syncTime = (date: string, clock: string) => {
    setDatePart(date);
    setTimePart(clock);
    const complete = Boolean(date && clock);
    setValue('time', complete ? `${date}T${clock}` : '', {
      shouldDirty: true,
      shouldValidate: complete,
    });
  };

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(async (values) => {
          setPermissionError(null);
          const permission =
            await ensureWebPushPermission();
          if (!permission.ok) {
            setPermissionError(permission.reason);
            return;
          }

          mutate(
            {
              eventId,
              type: 'web_push',
              status: 'pending',
              time: new Date(values.time).getTime() / 1000,
            },
            {
              onSuccess: (notification) => {
                reset(initialValues);
                setDatePart(today);
                setTimePart(initialClock);
                onSuccess?.(notification);
              },
            },
          );
        })(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormField
          id="notification-date"
          label="Дата"
          type="date"
          value={datePart}
          onChange={(event) =>
            syncTime(event.target.value, timePart)
          }
        />
        <FormField
          id="notification-clock"
          label="Время"
          type="time"
          value={timePart}
          onChange={(event) =>
            syncTime(datePart, event.target.value)
          }
        />
        {errors.time ? (
          <span
            role="alert"
            className="sm:col-span-2 text-sm text-red-700"
          >
            {errors.time.message}
          </span>
        ) : null}
      </div>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="notification-type"
          className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
        >
          Способ уведомления
        </label>
        <select
          id="notification-type"
          className="w-full border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
          {...register('type')}
        >
          {Object.entries(TYPE_LABELS).map(
            ([value, label]) => (
              <option
                key={value}
                value={value}
                disabled={value !== 'web_push'}
              >
                {label}
              </option>
            ),
          )}
        </select>
      </div>

      <p className="text-sm leading-5 text-[var(--ink)]/60">
        При сохранении браузер попросит разрешение на
        системные Push-уведомления.
      </p>

      {permissionError ? (
        <p
          role="alert"
          className="border-l-4 border-amber-600 bg-amber-50 px-4 py-3 text-sm leading-5 text-amber-900"
        >
          {permissionError}
        </p>
      ) : null}

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось создать уведомление. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      <div className="flex flex-col gap-2">
        <SubmitButton
          pending={isPending}
          pendingLabel="Сохраняем…"
        >
          {onCancel ? 'Сохранить' : 'Добавить уведомление'}
        </SubmitButton>
        {onCancel ? (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-sm border border-[var(--forest)]/25 bg-white px-4 py-3 text-sm font-bold text-[var(--forest)] hover:border-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
          >
            Отмена
          </button>
        ) : null}
      </div>
    </form>
  );
}
