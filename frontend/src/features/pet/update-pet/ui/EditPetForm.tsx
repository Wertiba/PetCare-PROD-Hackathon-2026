'use client';

import type { Pet } from '@src/entities/pet';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useForm } from 'react-hook-form';

import { useUpdatePetMutation } from '../model';

interface EditPetFormProps {
  onPendingChange?: (isPending: boolean) => void;
  onSuccess: () => void;
  pet: Pet;
}

interface EditPetValues {
  birthDate: string;
  name: string;
}

const toDateInputValue = (timestamp: number | null) =>
  timestamp
    ? new Date(timestamp * 1000).toISOString().slice(0, 10)
    : '';

export function EditPetForm({
  onPendingChange,
  onSuccess,
  pet,
}: EditPetFormProps) {
  const { mutate, isPending, error } =
    useUpdatePetMutation();
  const { register, handleSubmit, formState } =
    useForm<EditPetValues>({
      defaultValues: {
        name: pet.name,
        birthDate: toDateInputValue(pet.birthDate),
      },
    });

  const submit = (values: EditPetValues) => {
    onPendingChange?.(true);
    mutate(
      {
        id: pet.id,
        data: {
          name: values.name.trim(),
          ...(values.birthDate
            ? {
                birthDate:
                  new Date(values.birthDate).getTime() /
                  1000,
              }
            : {}),
        },
      },
      {
        onError: () => onPendingChange?.(false),
        onSuccess: () => {
          onPendingChange?.(false);
          onSuccess();
        },
      },
    );
  };

  return (
    <form
      className="flex flex-col gap-5"
      noValidate
      onSubmit={(event) => {
        void handleSubmit(submit)(event);
      }}
    >
      <FormField
        label="Кличка"
        error={formState.errors.name?.message}
        {...register('name', {
          required: 'Укажите кличку питомца',
          validate: (value) =>
            value.trim().length > 0 ||
            'Укажите кличку питомца',
        })}
      />
      <div className="rounded-sm border border-[var(--forest)]/20 bg-white px-4 py-3">
        <p className="text-xs font-semibold tracking-[0.08em] text-[var(--forest)]/60 uppercase">
          Вид и порода
        </p>
        <p className="mt-1 text-sm font-semibold text-[var(--forest)]">
          {pet.animal?.name ?? 'Не указано'} ·{' '}
          {pet.breed?.name ?? 'Не указано'}
        </p>
      </div>
      <FormField
        label="Дата рождения"
        type="date"
        {...register('birthDate')}
      />
      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось сохранить изменения. Попробуйте ещё
          раз.
        </p>
      ) : null}
      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Сохранить изменения
      </SubmitButton>
    </form>
  );
}
