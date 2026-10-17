'use client';

import {
  type Category,
  type CategoryKind,
  type CategoryType,
  type CategoryUnit,
  useGetCategoriesQuery,
} from '@src/entities/category';
import { useCreateCategoryMutation } from '@src/features/category/create-category';
import { useDeleteCategoryMutation } from '@src/features/category/delete-category';
import { useUpdateCategoryMutation } from '@src/features/category/update-category';
import { useState } from 'react';

import {
  ADMIN_DANGER_BUTTON_CLASSES,
  ADMIN_GHOST_BUTTON_CLASSES,
  ADMIN_PRIMARY_BUTTON_CLASSES,
  AdminConfirmDelete,
  AdminError,
  adminErrorMessage,
} from './AdminNameList';

const PAGE_SIZE = 100;

const IN_USE =
  'Категорией уже пользуются другие: её нельзя удалить, а тип и способ подсчёта нельзя менять.';

const TYPE_LABELS: Record<CategoryType, string> = {
  check: 'Отметка (да/нет)',
  number: 'Число',
  scale: 'Шкала 1–5',
};

const KIND_LABELS: Record<CategoryKind, string> = {
  sum: 'Сумма',
  avg: 'Среднее',
  last: 'Последнее',
  count: 'Количество',
  min: 'Минимум',
  max: 'Максимум',
};

const UNIT_LABELS: Record<CategoryUnit, string> = {
  none: 'без единиц',
  g: 'г',
  ml: 'мл',
  min: 'мин',
  m: 'м',
  times: 'раз',
  rub: '₽',
  points: 'баллы',
};

const SELECT_CLASSES =
  'w-full rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-2 text-sm font-bold text-[var(--forest)] focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)] disabled:opacity-60';

const INPUT_CLASSES =
  'w-full min-w-0 rounded-sm border border-[var(--ink)] bg-[var(--white)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]';

interface CategoryValues {
  name: string;
  type: CategoryType;
  kind: CategoryKind;
  unit: CategoryUnit;
}

const NEW_CATEGORY: CategoryValues = {
  name: '',
  type: 'number',
  kind: 'last',
  unit: 'none',
};

interface CategoryFieldsProps {
  idPrefix: string;
  values: CategoryValues;
  disabled: boolean;
  onChange: (values: CategoryValues) => void;
}

function CategoryFields({
  idPrefix,
  values,
  disabled,
  onChange,
}: CategoryFieldsProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <div className="flex flex-col gap-1.5 sm:col-span-2">
        <label
          htmlFor={`${idPrefix}-name`}
          className="text-sm font-semibold text-[var(--forest)]"
        >
          Название
        </label>
        <input
          id={`${idPrefix}-name`}
          value={values.name}
          maxLength={100}
          placeholder="Например, Прогулка"
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...values,
              name: event.target.value,
            })
          }
          className={INPUT_CLASSES}
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor={`${idPrefix}-type`}
          className="text-sm font-semibold text-[var(--forest)]"
        >
          Значение
        </label>
        <select
          id={`${idPrefix}-type`}
          value={values.type}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...values,
              type: event.target.value as CategoryType,
            })
          }
          className={SELECT_CLASSES}
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
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor={`${idPrefix}-kind`}
          className="text-sm font-semibold text-[var(--forest)]"
        >
          Подсчёт за период
        </label>
        <select
          id={`${idPrefix}-kind`}
          value={values.kind}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...values,
              kind: event.target.value as CategoryKind,
            })
          }
          className={SELECT_CLASSES}
        >
          {Object.entries(KIND_LABELS).map(
            ([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ),
          )}
        </select>
      </div>
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor={`${idPrefix}-unit`}
          className="text-sm font-semibold text-[var(--forest)]"
        >
          Единица
        </label>
        <select
          id={`${idPrefix}-unit`}
          value={values.unit}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...values,
              unit: event.target.value as CategoryUnit,
            })
          }
          className={SELECT_CLASSES}
        >
          {Object.entries(UNIT_LABELS).map(
            ([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ),
          )}
        </select>
      </div>
    </div>
  );
}

interface CategoryRowProps {
  category: Category;
  onDelete: () => void;
}

function CategoryRow({
  category,
  onDelete,
}: CategoryRowProps) {
  const update = useUpdateCategoryMutation();
  const [draft, setDraft] = useState<CategoryValues | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);

  if (draft) {
    return (
      <li className="py-4">
        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            const name = draft.name.trim();
            if (!name) return;
            setError(null);
            update.mutate(
              {
                id: category.id,
                data: {
                  name,
                  type: draft.type,
                  kind: draft.kind,
                  unit: draft.unit,
                },
              },
              {
                onSuccess: () => setDraft(null),
                onError: (cause) =>
                  setError(
                    adminErrorMessage(cause, IN_USE),
                  ),
              },
            );
          }}
          className="flex flex-col gap-3"
        >
          <CategoryFields
            idPrefix={`category-${category.id}`}
            values={draft}
            disabled={update.isPending}
            onChange={setDraft}
          />
          <AdminError error={error} />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={
                update.isPending || !draft.name.trim()
              }
              className={ADMIN_PRIMARY_BUTTON_CLASSES}
            >
              {update.isPending
                ? 'Сохраняем…'
                : 'Сохранить'}
            </button>
            <button
              type="button"
              onClick={() => {
                setError(null);
                setDraft(null);
              }}
              className={ADMIN_GHOST_BUTTON_CLASSES}
            >
              Отмена
            </button>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li className="flex flex-wrap items-center gap-x-3 gap-y-1 py-3">
      <div className="min-w-0 flex-1">
        <p className="truncate font-semibold text-[var(--forest)]">
          {category.name}
        </p>
        <p className="text-sm text-[var(--ink)]/55">
          {TYPE_LABELS[category.type]} ·{' '}
          {KIND_LABELS[category.kind].toLowerCase()} ·{' '}
          {UNIT_LABELS[category.unit]}
        </p>
      </div>
      {category.isSystem ? (
        <span className="rounded-sm bg-[var(--lime)] px-2 py-1 text-xs font-bold text-[var(--forest)]">
          базовая
        </span>
      ) : (
        <span className="rounded-sm bg-[var(--cream)] px-2 py-1 text-xs font-bold text-[var(--ink)]/55">
          пользовательская
        </span>
      )}
      <button
        type="button"
        onClick={() =>
          setDraft({
            name: category.name,
            type: category.type,
            kind: category.kind,
            unit: category.unit,
          })
        }
        className={ADMIN_GHOST_BUTTON_CLASSES}
      >
        Изменить
      </button>
      <button
        type="button"
        onClick={onDelete}
        className={ADMIN_DANGER_BUTTON_CLASSES}
      >
        Удалить
      </button>
    </li>
  );
}

export function AdminCategories() {
  const { data, isPending, isError } =
    useGetCategoriesQuery({ page: 0, size: PAGE_SIZE });
  const creation = useCreateCategoryMutation();
  const deletion = useDeleteCategoryMutation();
  const [values, setValues] =
    useState<CategoryValues>(NEW_CATEGORY);
  const [error, setError] = useState<string | null>(null);
  const [toDelete, setToDelete] = useState<Category | null>(
    null,
  );
  const categories = data?.items ?? [];

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.72fr)]">
      <section aria-labelledby="admin-categories-heading">
        <h2
          id="admin-categories-heading"
          className="text-xl font-black text-[var(--forest)]"
        >
          Категории замеров
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--ink)]/65">
          Категории общие для всех: вес, корм, самочувствие.
          Сначала идут базовые, затем созданные
          пользователями.
        </p>

        {isPending ? (
          <p
            role="status"
            className="mt-5 text-sm text-[var(--ink)]/60"
          >
            Загружаем категории…
          </p>
        ) : isError ? (
          <div className="mt-5">
            <AdminError error="Не удалось загрузить категории. Обновите страницу." />
          </div>
        ) : categories.length === 0 ? (
          <p className="mt-5 text-sm text-[var(--ink)]/60">
            Категорий пока нет. Добавьте первую.
          </p>
        ) : (
          <ul className="mt-4 divide-y divide-[var(--forest)]/10 border-y border-[var(--forest)]/10">
            {categories.map((category) => (
              <CategoryRow
                key={category.id}
                category={category}
                onDelete={() => {
                  deletion.reset();
                  setToDelete(category);
                }}
              />
            ))}
          </ul>
        )}
      </section>

      <section
        aria-labelledby="admin-category-add-heading"
        className="flex flex-col gap-4 border-t border-[var(--forest)]/15 pt-7 lg:border-t-0 lg:border-l lg:pl-8 lg:pt-0"
      >
        <h2
          id="admin-category-add-heading"
          className="text-xl font-black text-[var(--forest)]"
        >
          Новая категория
        </h2>
        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            const name = values.name.trim();
            if (!name) return;
            setError(null);
            creation.mutate(
              { ...values, name },
              {
                onSuccess: () => setValues(NEW_CATEGORY),
                onError: (cause) =>
                  setError(adminErrorMessage(cause)),
              },
            );
          }}
          className="flex flex-col gap-4"
        >
          <CategoryFields
            idPrefix="admin-category-new"
            values={values}
            disabled={creation.isPending}
            onChange={setValues}
          />
          <AdminError error={error} />
          <button
            type="submit"
            disabled={
              creation.isPending || !values.name.trim()
            }
            className={`${ADMIN_PRIMARY_BUTTON_CLASSES} self-start`}
          >
            {creation.isPending
              ? 'Добавляем…'
              : 'Добавить категорию'}
          </button>
        </form>
      </section>

      {toDelete ? (
        <AdminConfirmDelete
          title="Удалить категорию?"
          pending={deletion.isPending}
          error={
            deletion.error
              ? adminErrorMessage(deletion.error, IN_USE)
              : null
          }
          onClose={() => setToDelete(null)}
          onConfirm={() =>
            deletion.mutate(toDelete.id, {
              onSuccess: () => setToDelete(null),
            })
          }
        >
          Категория «{toDelete.name}» будет удалена вместе с
          вашими замерами в ней. Если ею пользуются другие,
          удалить не получится.
        </AdminConfirmDelete>
      ) : null}
    </div>
  );
}
