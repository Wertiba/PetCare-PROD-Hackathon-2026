// По образцу login/LoginForm.tsx.
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';

import { FormField, SubmitButton } from '../ui';
import {
  type IntervalInput,
  type IntervalValues,
  intervalSchema,
} from './validation';

export function IntervalForm() {
  const [isPending, setPending] = useState(false);
  const [error, setError] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<IntervalInput, unknown, IntervalValues>({
    defaultValues: { minutes: '' },
    mode: 'onTouched',
    resolver: zodResolver(intervalSchema),
  });

  useEffect(() => {
    void window.intervalApi
      .getPollMinutes()
      .then((minutes) =>
        reset({ minutes: String(minutes) }),
      );
  }, [reset]);

  const save = ({ minutes }: IntervalValues) => {
    setPending(true);
    setError(false);
    // On success the main process closes this window.
    window.intervalApi
      .savePollMinutes(minutes)
      .then(
        (ok) => setError(!ok),
        () => setError(true),
      )
      .finally(() => setPending(false));
  };

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(save)(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <FormField
        label="Проверять напоминания каждые, мин"
        type="number"
        inputMode="numeric"
        min={1}
        step={1}
        autoFocus
        error={errors.minutes?.message}
        {...register('minutes')}
      />

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить интервал. Попробуйте ещё раз.
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
