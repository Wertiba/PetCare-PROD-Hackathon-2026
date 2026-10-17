'use client';

import {
  type Breed,
  useGetAnimalsQuery,
  useGetBreedsQuery,
} from '@src/entities/pet';
import { useCreateBreedMutation } from '@src/features/breed/create-breed';
import { useDeleteBreedMutation } from '@src/features/breed/delete-breed';
import { useUpdateBreedMutation } from '@src/features/breed/update-breed';
import { useState } from 'react';

import {
  AdminAddForm,
  AdminConfirmDelete,
  AdminError,
  AdminNameRow,
  adminErrorMessage,
} from './AdminNameList';

const PAGE_SIZE = 100;

export function AdminBreeds() {
  const animalsQuery = useGetAnimalsQuery({
    page: 0,
    size: PAGE_SIZE,
    q: '',
  });
  const animals = animalsQuery.data?.items ?? [];
  const [chosenAnimalId, setChosenAnimalId] = useState('');
  const animal =
    animals.find((item) => item.id === chosenAnimalId) ??
    animals[0];
  const creation = useCreateBreedMutation();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.72fr)]">
      <section aria-labelledby="admin-breeds-heading">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2
            id="admin-breeds-heading"
            className="text-xl font-black text-[var(--forest)]"
          >
            Породы
          </h2>
          <div className="flex items-center gap-2">
            <label
              htmlFor="admin-breeds-animal"
              className="text-sm font-semibold text-[var(--ink)]/65"
            >
              Вид
            </label>
            <select
              id="admin-breeds-animal"
              value={animal?.id ?? ''}
              disabled={animals.length === 0}
              onChange={(event) => {
                setError(null);
                setChosenAnimalId(event.target.value);
              }}
              className="rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
            >
              {animals.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <p className="mt-2 text-sm leading-6 text-[var(--ink)]/65">
          Породы показываются по одному виду. Удалённая
          порода исчезает у питомцев, сами питомцы остаются.
        </p>

        {animalsQuery.isPending ? (
          <p
            role="status"
            className="mt-5 text-sm text-[var(--ink)]/60"
          >
            Загружаем виды…
          </p>
        ) : animalsQuery.isError ? (
          <div className="mt-5">
            <AdminError error="Не удалось загрузить виды. Обновите страницу." />
          </div>
        ) : animal ? (
          <AdminBreedList
            key={animal.id}
            animalId={animal.id}
            animalName={animal.name}
            onError={setError}
          />
        ) : (
          <p className="mt-5 text-sm text-[var(--ink)]/60">
            Сначала добавьте вид на вкладке «Виды».
          </p>
        )}
      </section>

      <section
        aria-labelledby="admin-breed-add-heading"
        className="flex flex-col gap-4 border-t border-[var(--forest)]/15 pt-7 lg:border-t-0 lg:border-l lg:pl-8 lg:pt-0"
      >
        <h2
          id="admin-breed-add-heading"
          className="text-xl font-black text-[var(--forest)]"
        >
          Новая порода
        </h2>
        <p className="text-sm leading-6 text-[var(--ink)]/65">
          {animal
            ? `Добавится к виду «${animal.name}».`
            : 'Сначала нужен хотя бы один вид.'}
        </p>
        <AdminAddForm
          id="admin-breed-name"
          label="Название породы"
          placeholder="Например, Сиамская"
          pending={creation.isPending}
          disabled={!animal}
          onAdd={(name, reset) => {
            if (!animal) return;
            setError(null);
            creation.mutate(
              { animalId: animal.id, name },
              {
                onSuccess: reset,
                onError: (cause) =>
                  setError(adminErrorMessage(cause)),
              },
            );
          }}
        />
        <AdminError error={error} />
      </section>
    </div>
  );
}

interface AdminBreedListProps {
  animalId: string;
  animalName: string;
  onError: (error: string | null) => void;
}

function AdminBreedList({
  animalId,
  animalName,
  onError,
}: AdminBreedListProps) {
  const { data, isPending, isError } = useGetBreedsQuery({
    page: 0,
    size: PAGE_SIZE,
    animalId,
    q: '',
  });
  const update = useUpdateBreedMutation();
  const deletion = useDeleteBreedMutation();
  const [toDelete, setToDelete] = useState<Breed | null>(
    null,
  );
  const breeds = data?.items ?? [];

  if (isPending) {
    return (
      <p
        role="status"
        className="mt-5 text-sm text-[var(--ink)]/60"
      >
        Загружаем породы…
      </p>
    );
  }

  if (isError) {
    return (
      <div className="mt-5">
        <AdminError error="Не удалось загрузить породы. Обновите страницу." />
      </div>
    );
  }

  if (breeds.length === 0) {
    return (
      <p className="mt-5 text-sm text-[var(--ink)]/60">
        У вида «{animalName}» пока нет пород.
      </p>
    );
  }

  return (
    <>
      <ul className="mt-4 divide-y divide-[var(--forest)]/10 border-y border-[var(--forest)]/10">
        {breeds.map((breed) => (
          <AdminNameRow
            key={breed.id}
            id={breed.id}
            name={breed.name}
            isSeeded={breed.createdBy === null}
            pending={
              update.isPending &&
              update.variables.id === breed.id
            }
            onRename={(name, done) => {
              onError(null);
              update.mutate(
                { id: breed.id, data: { name } },
                {
                  onSuccess: done,
                  onError: (cause) =>
                    onError(adminErrorMessage(cause)),
                },
              );
            }}
            onDelete={() => {
              deletion.reset();
              setToDelete(breed);
            }}
          />
        ))}
      </ul>

      {toDelete ? (
        <AdminConfirmDelete
          title="Удалить породу?"
          pending={deletion.isPending}
          error={
            deletion.error
              ? adminErrorMessage(deletion.error)
              : null
          }
          onClose={() => setToDelete(null)}
          onConfirm={() =>
            deletion.mutate(toDelete.id, {
              onSuccess: () => setToDelete(null),
            })
          }
        >
          Порода «{toDelete.name}» будет удалена. Питомцы
          этой породы останутся, но без породы.
        </AdminConfirmDelete>
      ) : null}
    </>
  );
}
