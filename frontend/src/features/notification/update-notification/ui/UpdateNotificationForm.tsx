'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import type { Notification } from '@src/entities/notification';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useForm } from 'react-hook-form';

import { useUpdateNotificationMutation } from '../model/update-notification.mutation';
import {
  type UpdateNotificationValues,
  updateNotificationSchema,
} from '../model/validation';

const TYPE_LABELS: Record<
  UpdateNotificationValues['type'],
  string
> = {
  app: 'В приложении',
  telegram: 'Telegram',
  web_push: 'Push в браузере',
};

const toDateTimeInputValue = (timestamp: number) => {
  const date = new Date(timestamp * 1000);
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 16);
};

interface UpdateNotificationFormProps {
  notification: Notification;
  onSuccess?: (notification: Notification) => void;
}

export function UpdateNotificationForm({
  notification,
  onSuccess,
}: UpdateNotificationFormProps) {
  const { mutate, isPending, error } =
    useUpdateNotificationMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UpdateNotificationValues>({
    defaultValues: {
      type: notification.type,
      time: toDateTimeInputValue(notification.time),
    },
    mode: 'onTouched',
    resolver: zodResolver(updateNotificationSchema),
  });

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) =>
          mutate(
            {
              id: notification.id,
              data: {
                type: values.type,
                time:
                  new Date(values.time).getTime() / 1000,
              },
            },
            { onSuccess },
          ),
        )(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <FormField
        id={`notification-time-${notification.id}`}
        label="Когда напомнить"
        type="datetime-local"
        error={errors.time?.message}
        {...register('time')}
      />

      <div className="flex flex-col gap-2">
        <label
          htmlFor={`notification-type-${notification.id}`}
          className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
        >
          Способ уведомления
        </label>
        <select
          id={`notification-type-${notification.id}`}
          className="w-full border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
          {...register('type')}
        >
          {Object.entries(TYPE_LABELS).map(
            ([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ),
          )}
        </select>
      </div>

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить уведомление. Проверьте данные
          и попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Сохранить
      </SubmitButton>
    </form>
  );
}
