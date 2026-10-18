'use client';

import {
  useGeneratePetAvatarMutation,
  useSelectPetAvatarMutation,
  useUploadPetPhotoMutation,
} from '@src/features/pet/upload-photo/model/upload-pet-photo.mutation';
import { Dialog } from '@src/shared/ui';
import { useState } from 'react';

type AvatarChoice = 'photo' | 'generated';

interface PetPhotoDialogProps {
  onClose: () => void;
  petId: string;
}

export function PetPhotoDialog({
  onClose,
  petId,
}: PetPhotoDialogProps) {
  const uploadPhoto = useUploadPetPhotoMutation();
  const generateAvatar = useGeneratePetAvatarMutation();
  const selectAvatar = useSelectPetAvatarMutation();
  const [choice, setChoice] =
    useState<AvatarChoice>('photo');
  const [file, setFile] = useState<File | null>(null);
  const [avatarPrompt, setAvatarPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const isPending =
    uploadPhoto.isPending ||
    generateAvatar.isPending ||
    selectAvatar.isPending;

  const submit = async () => {
    if (!file) {
      setError('Выберите исходную фотографию питомца.');
      return;
    }

    setError(null);
    try {
      await uploadPhoto.mutateAsync({ petId, file });

      if (choice === 'generated') {
        await generateAvatar.mutateAsync({
          petId,
          prompt: avatarPrompt.trim(),
        });
        await selectAvatar.mutateAsync({
          petId,
          source: 'generated',
        });
      } else {
        await selectAvatar.mutateAsync({
          petId,
          source: 'photo',
        });
      }

      onClose();
    } catch {
      setError(
        choice === 'generated'
          ? 'Не удалось создать ИИ-аватар. Попробуйте ещё раз.'
          : 'Не удалось обновить фото. Проверьте файл и попробуйте ещё раз.',
      );
    }
  };

  return (
    <Dialog
      labelledBy="pet-photo-dialog-title"
      onClose={onClose}
    >
      <div className="w-xl max-w-full p-5 sm:p-6">
        <div className="flex min-w-0 items-start justify-between gap-5 border-b border-[var(--forest)]/15 pb-4">
          <div className="min-w-0">
            <p className="text-xs font-bold tracking-[.12em] text-[var(--forest)]/60 uppercase">
              Профиль питомца
            </p>
            <h2
              id="pet-photo-dialog-title"
              className="mt-1 break-words text-2xl font-black text-[var(--forest)]"
            >
              Изменить фото
            </h2>
            <p className="mt-1 break-words text-sm text-[var(--ink)]/60">
              Выберите обычное фото или ИИ-аватар на его
              основе.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            aria-label="Закрыть"
            className="grid size-9 shrink-0 place-items-center border border-[var(--forest)] text-xl text-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            ×
          </button>
        </div>

        <fieldset className="mt-5">
          <legend className="text-sm font-bold text-[var(--forest)]">
            Какое изображение показать
          </legend>
          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            {(
              [
                [
                  'photo',
                  'Обычное фото',
                  'Покажем выбранный снимок',
                ],
                [
                  'generated',
                  'ИИ-аватар',
                  'Создадим по этому снимку',
                ],
              ] as const
            ).map(([value, title, description]) => {
              const selected = choice === value;
              return (
                <button
                  key={value}
                  type="button"
                  aria-pressed={selected}
                  disabled={isPending}
                  onClick={() => {
                    setChoice(value);
                    setError(null);
                  }}
                  className={`min-h-24 border p-3 text-left transition-colors disabled:cursor-not-allowed disabled:opacity-55 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] ${
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
        </fieldset>

        <div className="mt-5">
          <label
            htmlFor="replacement-pet-photo"
            className="block text-sm font-bold text-[var(--forest)]"
          >
            Исходная фотография
          </label>
          <input
            id="replacement-pet-photo"
            type="file"
            accept="image/*"
            disabled={isPending}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setError(null);
            }}
            className="mt-2 block w-full cursor-pointer border border-dashed border-[var(--forest)]/45 bg-[var(--cream)] px-3 py-2 text-sm text-[var(--ink)] file:mr-3 file:border-0 file:bg-[var(--forest)] file:px-3 file:py-1.5 file:text-sm file:font-bold file:text-white disabled:cursor-not-allowed disabled:opacity-50"
          />
          <p className="mt-1.5 text-xs text-[var(--ink)]/55">
            {choice === 'generated'
              ? 'Сначала загрузим фото, затем ИИ подготовит аватар.'
              : 'Новое фото заменит текущее изображение питомца.'}
          </p>
        </div>

        {choice === 'generated' ? (
          <div className="mt-5">
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
              disabled={isPending}
              rows={3}
              placeholder="Например: в красном шарфе"
              className="mt-2 block w-full resize-y border border-[var(--forest)]/45 bg-white px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink)]/40 focus:border-[var(--forest)] focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
        ) : null}

        {generateAvatar.isPending ? (
          <div
            role="status"
            aria-live="polite"
            className="mt-5 flex items-center gap-3 border-l-4 border-[var(--forest)] bg-[var(--lime)]/35 px-4 py-3 text-sm font-semibold text-[var(--forest)]"
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
            ИИ создаёт аватар питомца…
          </div>
        ) : null}

        {error ? (
          <p
            role="alert"
            className="mt-5 border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm font-semibold text-red-800"
          >
            {error}
          </p>
        ) : null}

        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="min-h-11 border border-[var(--forest)] px-4 py-2 text-sm font-bold text-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            Отмена
          </button>
          <button
            type="button"
            onClick={() => void submit()}
            disabled={isPending}
            className="min-h-11 bg-[var(--forest)] px-4 py-2 text-sm font-black text-white shadow-[3px_3px_0_var(--lime)] disabled:cursor-not-allowed disabled:opacity-55"
          >
            {generateAvatar.isPending
              ? 'Создаём ИИ-аватар…'
              : choice === 'generated'
                ? 'Создать ИИ-аватар'
                : 'Сохранить фото'}
          </button>
        </div>
      </div>
    </Dialog>
  );
}
