'use client';

import {
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useRef, useState } from 'react';

import { useUpdateFullNameMutation } from '../model/use-update-full-name-mutation';
import { updateFullNameSchema } from '../model/validation';

export function UpdateFullNameForm() {
  const user = useUserStore(selectUser);
  const { mutate, error, isPending, isSuccess } =
    useUpdateFullNameMutation();
  const inputRef = useRef<HTMLInputElement>(null);
  const [validationError, setValidationError] = useState<
    string | null
  >(null);
  const [isSaved, setIsSaved] = useState(false);

  const onSubmit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    const value = new FormData(event.currentTarget).get(
      'fullName',
    );
    const fullName =
      typeof value === 'string' ? value.trim() : '';
    const validation = updateFullNameSchema.safeParse({
      fullName,
    });

    if (!validation.success) {
      setValidationError(
        validation.error.issues[0]?.message ??
          'Введите корректное полное имя.',
      );
      return;
    }

    setValidationError(null);
    setIsSaved(false);

    mutate(
      { fullName: validation.data.fullName },
      {
        onSuccess: (updatedUser) => {
          if (inputRef.current) {
            inputRef.current.value = updatedUser.fullName;
          }
          setIsSaved(true);
        },
      },
    );
  };

  return (
    <form
      noValidate
      onSubmit={onSubmit}
      className="mt-5 flex max-w-xl flex-col gap-4"
    >
      <FormField
        key={user?.id ?? 'no-user'}
        ref={inputRef}
        label="Полное имя"
        name="fullName"
        type="text"
        autoComplete="name"
        placeholder="Как к вам обращаться"
        defaultValue={user?.fullName ?? ''}
        error={validationError ?? undefined}
        disabled={!user || isPending}
        onInput={() => setIsSaved(false)}
      />

      {error && !validationError ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить имя. Проверьте соединение и
          попробуйте ещё раз.
        </p>
      ) : null}

      {isSuccess && isSaved ? (
        <p
          role="status"
          className="text-sm font-semibold text-[var(--forest)]"
        >
          Имя сохранено.
        </p>
      ) : null}

      <div className="max-w-56">
        <SubmitButton
          pending={isPending}
          pendingLabel="Сохраняем…"
        >
          Сохранить имя
        </SubmitButton>
      </div>
    </form>
  );
}
