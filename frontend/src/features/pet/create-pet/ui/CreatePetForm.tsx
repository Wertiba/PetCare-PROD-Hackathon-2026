'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import {
  AnimalSelect,
  BreedSelect,
  type Pet,
} from '@src/entities/pet';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useEffect } from 'react';
import {
  Controller,
  useForm,
  useWatch,
} from 'react-hook-form';

import { useCreatePetMutation } from '../model/create-pet.mutation';
import {
  type CreatePetValues,
  createPetSchema,
} from '../model/validation';

const INITIAL_VALUES: Partial<CreatePetValues> = {
  name: '',
  animalId: '',
  breedId: '',
  birthDate: '',
};

interface CreatePetFormProps {
  onPendingChange?: (isPending: boolean) => void;
  onSuccess?: (pet: Pet) => void;
}

export function CreatePetForm({
  onPendingChange,
  onSuccess,
}: CreatePetFormProps) {
  const { mutate, isPending, error } =
    useCreatePetMutation();
  const {
    register,
    control,
    setValue,
    handleSubmit,
    formState: { errors },
  } = useForm<CreatePetValues>({
    defaultValues: INITIAL_VALUES,
    mode: 'onTouched',
    resolver: zodResolver(createPetSchema),
  });

  const animalId = useWatch({ control, name: 'animalId' });

  useEffect(() => {
    onPendingChange?.(isPending);
  }, [isPending, onPendingChange]);

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) =>
          mutate(
            {
              name: values.name,
              breedId: values.breedId,
              birthDate:
                new Date(values.birthDate).getTime() / 1000,
            },
            { onSuccess },
          ),
        )(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <FormField
        label="Кличка"
        type="text"
        placeholder="Введите кличку"
        error={errors.name?.message}
        {...register('name')}
      />

      <Controller
        control={control}
        name="animalId"
        render={({ field }) => (
          <AnimalSelect
            value={field.value}
            onChange={(value) => {
              field.onChange(value);
              setValue('breedId', '');
            }}
            onBlur={field.onBlur}
            error={errors.animalId?.message}
          />
        )}
      />

      {animalId ? (
        <Controller
          control={control}
          name="breedId"
          render={({ field }) => (
            <BreedSelect
              key={animalId}
              animalId={animalId}
              value={field.value}
              onChange={field.onChange}
              onBlur={field.onBlur}
              error={errors.breedId?.message}
            />
          )}
        />
      ) : (
        <FormField
          label="Порода"
          type="text"
          placeholder="Сначала выберите вид животного"
          disabled
        />
      )}
      <FormField
        label="Дата рождения"
        type="date"
        error={errors.birthDate?.message}
        {...register('birthDate')}
      />

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось добавить питомца. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Сохраняем…"
      >
        Добавить питомца
      </SubmitButton>
    </form>
  );
}
