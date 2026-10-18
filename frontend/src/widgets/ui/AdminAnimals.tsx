'use client';

import {
  type Animal,
  useGetAnimalsQuery,
} from '@src/entities/pet';
import { useCreateAnimalMutation } from '@src/features/animal/create-animal';
import { useDeleteAnimalMutation } from '@src/features/animal/delete-animal';
import { useUpdateAnimalMutation } from '@src/features/animal/update-animal';
import { useState } from 'react';

import {
  AdminAddForm,
  AdminConfirmDelete,
  AdminError,
  AdminNameRow,
  adminErrorMessage,
} from './AdminNameList';

const PAGE_SIZE = 100;

export function AdminAnimals() {
  const { data, isPending, isError } = useGetAnimalsQuery({
    page: 0,
    size: PAGE_SIZE,
    q: '',
  });
  const creation = useCreateAnimalMutation();
  const update = useUpdateAnimalMutation();
  const deletion = useDeleteAnimalMutation();
  const [error, setError] = useState<string | null>(null);
  const [toDelete, setToDelete] = useState<Animal | null>(
    null,
  );
  const animals = data?.items ?? [];

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.72fr)]">
      <section aria-labelledby="admin-animals-heading">
        <h2
          id="admin-animals-heading"
          className="text-xl font-black text-[var(--forest)]"
        >
          Виды животных
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--ink)]/65">
          Вид выбирают при создании питомца. Порода всегда
          относится к одному виду.
        </p>

        {isPending ? (
          <p
            role="status"
            className="mt-5 text-sm text-[var(--ink)]/60"
          >
            Загружаем виды…
          </p>
        ) : isError ? (
          <div className="mt-5">
            <AdminError error="Не удалось загрузить виды. Обновите страницу." />
          </div>
        ) : animals.length === 0 ? (
          <p className="mt-5 text-sm text-[var(--ink)]/60">
            Видов пока нет. Добавьте первый.
          </p>
        ) : (
          <ul className="mt-4 divide-y divide-[var(--forest)]/10 border-y border-[var(--forest)]/10">
            {animals.map((animal) => (
              <AdminNameRow
                key={animal.id}
                id={animal.id}
                name={animal.name}
                isSeeded={animal.createdBy === null}
                pending={
                  update.isPending &&
                  update.variables.id === animal.id
                }
                onRename={(name, done) => {
                  setError(null);
                  update.mutate(
                    { id: animal.id, data: { name } },
                    {
                      onSuccess: done,
                      onError: (cause) =>
                        setError(adminErrorMessage(cause)),
                    },
                  );
                }}
                onDelete={() => {
                  deletion.reset();
                  setToDelete(animal);
                }}
              />
            ))}
          </ul>
        )}
      </section>

      <section
        aria-labelledby="admin-animal-add-heading"
        className="flex flex-col gap-4 border-t border-[var(--forest)]/15 pt-7 lg:border-t-0 lg:border-l lg:pl-8 lg:pt-0"
      >
        <h2
          id="admin-animal-add-heading"
          className="text-xl font-black text-[var(--forest)]"
        >
          Новый вид
        </h2>
        <AdminAddForm
          id="admin-animal-name"
          label="Название вида"
          placeholder="Например, Хорёк"
          pending={creation.isPending}
          onAdd={(name, reset) => {
            setError(null);
            creation.mutate(
              { name },
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

      {toDelete ? (
        <AdminConfirmDelete
          title="Удалить вид?"
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
          Вид «{toDelete.name}» будет удалён вместе со всеми
          его породами. Питомцы этих пород останутся, но без
          породы.
        </AdminConfirmDelete>
      ) : null}
    </div>
  );
}
