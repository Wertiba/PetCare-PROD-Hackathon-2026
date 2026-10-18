'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import {
  AnimalSelect,
  BreedSelect,
  type Pet,
} from '@src/entities/pet';
import { FormField, SubmitButton } from '@src/shared/ui';
import { useEffect, useState } from 'react';
import {
  Controller,
  useForm,
  useWatch,
} from 'react-hook-form';

import {
  useGeneratePetAvatarMutation,
  useSelectPetAvatarMutation,
  useUploadPetPhotoMutation,
} from '../../upload-photo/model/upload-pet-photo.mutation';
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

type AvatarChoice = 'none' | 'photo' | 'generated';

interface CreatePetFormProps {
  onPendingChange?: (isPending: boolean) => void;
  onSuccess?: (pet: Pet) => void;
}

export function CreatePetForm({
  onPendingChange,
  onSuccess,
}: CreatePetFormProps) {
  const { mutateAsync, isPending, error } =
    useCreatePetMutation();
  const uploadPhoto = useUploadPetPhotoMutation();
  const generateAvatar = useGeneratePetAvatarMutation();
  const selectAvatar = useSelectPetAvatarMutation();
  const [avatarChoice, setAvatarChoice] =
    useState<AvatarChoice>('none');
  const [photo, setPhoto] = useState<File | null>(null);
  const [avatarPrompt, setAvatarPrompt] = useState('');
  const [photoError, setPhotoError] = useState<
    string | null
  >(null);
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
    onPendingChange?.(
      isPending ||
        uploadPhoto.isPending ||
        generateAvatar.isPending ||
        selectAvatar.isPending,
    );
  }, [
    generateAvatar.isPending,
    isPending,
    onPendingChange,
    selectAvatar.isPending,
    uploadPhoto.isPending,
  ]);

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(async (values) => {
          setPhotoError(null);
          if (avatarChoice !== 'none' && !photo) {
            setPhotoError(
              'Выберите фотографию, чтобы использовать её или создать ИИ-аватар.',
            );
            return;
          }

          let pet: Pet;
          try {
            pet = await mutateAsync({
              name: values.name,
              breedId: values.breedId,
              birthDate:
                new Date(values.birthDate).getTime() / 1000,
            });
          } catch {
            return;
          }

          if (avatarChoice !== 'none' && photo) {
            try {
              const petWithPhoto =
                await uploadPhoto.mutateAsync({
                  petId: pet.id,
                  file: photo,
                });

              if (avatarChoice === 'generated') {
                await generateAvatar.mutateAsync({
                  petId: pet.id,
                  prompt: avatarPrompt.trim(),
                });
                const petWithAvatar =
                  await selectAvatar.mutateAsync({
                    petId: pet.id,
                    source: 'generated',
                  });
                onSuccess?.(petWithAvatar);
                return;
              }

              const updatedPet =
                await selectAvatar.mutateAsync({
                  petId: pet.id,
                  source: 'photo',
                });
              onSuccess?.(updatedPet ?? petWithPhoto);
            } catch {
              setPhotoError(
                avatarChoice === 'generated'
                  ? 'Питомец создан, но ИИ-аватар не удалось подготовить. Попробуйте изменить фото на главной странице питомца.'
                  : 'Питомец создан, но фото не загрузилось. Его можно добавить на главной странице питомца.',
              );
            }
            return;
          }

          onSuccess?.(pet);
        })(event);
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

      <fieldset>
        <legend className="text-sm font-bold text-[var(--forest)]">
          Оформление профиля питомца{' '}
          <span className="font-normal text-[var(--ink)]/55">
            (необязательно)
          </span>
        </legend>
        <div className="mt-2 grid gap-2 sm:grid-cols-3">
          {(
            [
              ['none', 'Без изображения', 'Добавите позже'],
              [
                'photo',
                'Обычное фото',
                'Покажем выбранное фото',
              ],
              [
                'generated',
                'ИИ-аватар',
                'Создадим из фотографии',
              ],
            ] as const
          ).map(([value, title, description]) => {
            const selected = avatarChoice === value;
            return (
              <button
                key={value}
                type="button"
                aria-pressed={selected}
                onClick={() => {
                  setAvatarChoice(value);
                  setPhotoError(null);
                }}
                className={`min-h-24 border p-3 text-left transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] ${
                  selected
                    ? 'border-[var(--forest)] bg-[var(--lime)]/40 text-[var(--forest)]'
                    : 'border-[var(--forest)]/20 bg-white text-[var(--ink)] hover:bg-[var(--cream)]'
                }`}
              >
                <span className="block text-sm font-black">
                  {title}
                </span>
                <span className="mt-1 block text-xs leading-5 opacity-70">
                  {description}
                </span>
              </button>
            );
          })}
        </div>

        {avatarChoice !== 'none' ? (
          <div className="mt-3">
            <label
              htmlFor="pet-photo"
              className="block text-sm font-bold text-[var(--forest)]"
            >
              Исходная фотография
            </label>
            <input
              id="pet-photo"
              type="file"
              accept="image/*"
              onChange={(event) => {
                setPhoto(event.target.files?.[0] ?? null);
                setPhotoError(null);
              }}
              className="mt-2 block w-full cursor-pointer border border-dashed border-[var(--forest)]/45 bg-[var(--cream)] px-3 py-2 text-sm text-[var(--ink)] file:mr-3 file:border-0 file:bg-[var(--forest)] file:px-3 file:py-1.5 file:text-sm file:font-bold file:text-white"
            />
            <p className="mt-1.5 text-xs text-[var(--ink)]/55">
              {avatarChoice === 'generated'
                ? 'Загрузим фото, затем создадим на его основе ИИ-аватар.'
                : 'Это изображение будет показано в профиле питомца.'}
            </p>
          </div>
        ) : null}

        {avatarChoice === 'generated' ? (
          <div className="mt-3">
            <label
              htmlFor="avatar-prompt"
              className="block text-sm font-bold text-[var(--forest)]"
            >
              Пожелание для ИИ-аватара{' '}
              <span className="font-normal text-[var(--ink)]/55">
                (необязательно)
              </span>
            </label>
            <textarea
              id="avatar-prompt"
              value={avatarPrompt}
              onChange={(event) =>
                setAvatarPrompt(event.target.value)
              }
              rows={3}
              placeholder="Например: в красном шарфе"
              className="mt-2 block w-full resize-y border border-[var(--forest)]/45 bg-white px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink)]/40 focus:border-[var(--forest)] focus:outline-none"
            />
          </div>
        ) : null}
      </fieldset>

      {generateAvatar.isPending ? (
        <div
          role="status"
          aria-live="polite"
          className="flex items-center gap-3 border-l-4 border-[var(--forest)] bg-[var(--lime)]/35 px-4 py-3 text-sm font-semibold text-[var(--forest)]"
        >
          <span className="grid size-6 shrink-0 place-items-center animate-spin">
            <svg
              aria-hidden="true"
              className="size-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M20 12a8 8 0 1 1-2.34-5.66" />
              <path d="M20 4v6h-6" />
            </svg>
          </span>
          ИИ создаёт аватар питомца… Это может занять
          несколько секунд.
        </div>
      ) : null}

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось добавить питомца. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      {photoError ? (
        <p
          role="alert"
          className="border-l-4 border-amber-600 bg-amber-50 px-4 py-3 text-sm leading-5 text-amber-900"
        >
          {photoError}
        </p>
      ) : null}

      <SubmitButton
        pending={
          isPending ||
          uploadPhoto.isPending ||
          generateAvatar.isPending ||
          selectAvatar.isPending
        }
        pendingLabel={
          generateAvatar.isPending
            ? 'Создаём ИИ-аватар…'
            : 'Сохраняем…'
        }
      >
        Добавить питомца
      </SubmitButton>
    </form>
  );
}
