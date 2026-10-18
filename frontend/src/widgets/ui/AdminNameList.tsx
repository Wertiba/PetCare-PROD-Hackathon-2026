'use client';

import { Dialog } from '@src/shared/ui';
import { isAxiosError } from 'axios';
import { useState } from 'react';

const INPUT_CLASSES =
  'w-full min-w-0 rounded-sm border border-[var(--ink)] bg-[var(--white)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]';

export const ADMIN_PRIMARY_BUTTON_CLASSES =
  'shrink-0 cursor-pointer rounded-sm border border-[var(--ink)] bg-[var(--lime)] px-4 py-2 text-sm font-bold text-[var(--forest)] shadow-[3px_3px_0_var(--ink)] transition-all enabled:hover:translate-x-0.5 enabled:hover:translate-y-0.5 enabled:hover:shadow-[1px_1px_0_var(--ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50';

export const ADMIN_GHOST_BUTTON_CLASSES =
  'shrink-0 cursor-pointer rounded-sm border border-[var(--forest)]/30 px-3 py-2 text-sm font-bold text-[var(--forest)] transition-colors hover:bg-[var(--cream)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50';

export const ADMIN_DANGER_BUTTON_CLASSES =
  'shrink-0 cursor-pointer rounded-sm px-3 py-2 text-sm font-bold text-red-800 transition-colors hover:bg-red-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-800 disabled:cursor-not-allowed disabled:opacity-50';

/** The API answers in English, so admin errors are worded by status. */
export function adminErrorMessage(
  error: unknown,
  conflict = 'Запись с таким названием уже есть.',
) {
  const status = isAxiosError(error)
    ? error.response?.status
    : undefined;
  if (status === 409) return conflict;
  if (status === 403)
    return 'Недостаточно прав: нужен аккаунт администратора.';
  if (status === 404)
    return 'Запись уже удалена. Обновите страницу.';
  if (status === 422)
    return 'Проверьте поля: название от 1 до 100 символов.';
  return 'Не удалось сохранить. Проверьте соединение и попробуйте ещё раз.';
}

export function AdminError({
  error,
}: {
  error: string | null;
}) {
  if (!error) return null;

  return (
    <p
      role="alert"
      className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
    >
      {error}
    </p>
  );
}

interface AdminAddFormProps {
  id: string;
  label: string;
  placeholder: string;
  pending: boolean;
  disabled?: boolean;
  onAdd: (name: string, reset: () => void) => void;
}

export function AdminAddForm({
  id,
  label,
  placeholder,
  pending,
  disabled = false,
  onAdd,
}: AdminAddFormProps) {
  const [name, setName] = useState('');

  return (
    <form
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        const trimmed = name.trim();
        if (trimmed) onAdd(trimmed, () => setName(''));
      }}
      className="flex flex-col gap-2"
    >
      <label
        htmlFor={id}
        className="text-sm font-semibold text-[var(--forest)]"
      >
        {label}
      </label>
      <div className="flex gap-2">
        <input
          id={id}
          value={name}
          maxLength={100}
          placeholder={placeholder}
          disabled={disabled || pending}
          onChange={(event) => setName(event.target.value)}
          className={INPUT_CLASSES}
        />
        <button
          type="submit"
          disabled={disabled || pending || !name.trim()}
          className={ADMIN_PRIMARY_BUTTON_CLASSES}
        >
          {pending ? 'Добавляем…' : 'Добавить'}
        </button>
      </div>
    </form>
  );
}

interface AdminNameRowProps {
  id: string;
  name: string;
  pending: boolean;
  onRename: (name: string, done: () => void) => void;
  onDelete: () => void;
}

export function AdminNameRow({
  id,
  name,
  pending,
  onRename,
  onDelete,
}: AdminNameRowProps) {
  const [draft, setDraft] = useState<string | null>(null);

  if (draft !== null) {
    return (
      <li className="py-3">
        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            const trimmed = draft.trim();
            if (!trimmed || trimmed === name) {
              setDraft(null);
              return;
            }
            onRename(trimmed, () => setDraft(null));
          }}
          className="flex flex-wrap gap-2"
        >
          <label
            className="sr-only"
            htmlFor={`rename-${id}`}
          >
            Новое название для «{name}»
          </label>
          <input
            id={`rename-${id}`}
            value={draft}
            maxLength={100}
            autoFocus
            disabled={pending}
            onChange={(event) =>
              setDraft(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === 'Escape') setDraft(null);
            }}
            className={`${INPUT_CLASSES} flex-1`}
          />
          <button
            type="submit"
            disabled={pending || !draft.trim()}
            className={ADMIN_PRIMARY_BUTTON_CLASSES}
          >
            {pending ? 'Сохраняем…' : 'Сохранить'}
          </button>
          <button
            type="button"
            onClick={() => setDraft(null)}
            className={ADMIN_GHOST_BUTTON_CLASSES}
          >
            Отмена
          </button>
        </form>
      </li>
    );
  }

  return (
    <li className="flex items-center gap-3 py-3">
      <span className="min-w-0 flex-1 truncate font-semibold text-[var(--forest)]">
        {name}
      </span>
      <button
        type="button"
        onClick={() => setDraft(name)}
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

interface AdminConfirmDeleteProps {
  title: string;
  children: React.ReactNode;
  pending: boolean;
  error: string | null;
  onConfirm: () => void;
  onClose: () => void;
}

export function AdminConfirmDelete({
  title,
  children,
  pending,
  error,
  onConfirm,
  onClose,
}: AdminConfirmDeleteProps) {
  return (
    <Dialog
      labelledBy="admin-delete-title"
      onClose={onClose}
    >
      <div className="mx-auto w-full max-w-md p-5 sm:p-6">
        <div className="mb-5 flex justify-between border-b border-[var(--forest)]/15 pb-4">
          <div>
            <p className="text-xs font-bold tracking-[.12em] text-[var(--forest)]/60 uppercase">
              Администрирование
            </p>
            <h2
              id="admin-delete-title"
              className="mt-1 text-2xl font-black text-[var(--forest)]"
            >
              {title}
            </h2>
          </div>
          <button
            onClick={onClose}
            type="button"
            aria-label="Закрыть"
            className="size-9 rounded-sm border border-[var(--forest)]"
          >
            ×
          </button>
        </div>
        <div className="text-sm leading-6 text-[var(--ink)]/80">
          {children}
        </div>
        <div className="mt-4">
          <AdminError error={error} />
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-sm border border-[var(--forest)] px-4 py-2"
          >
            Отмена
          </button>
          <button
            type="button"
            disabled={pending}
            onClick={onConfirm}
            className="rounded-sm bg-red-800 px-4 py-2 text-white disabled:opacity-60"
          >
            {pending ? 'Удаляем…' : 'Удалить'}
          </button>
        </div>
      </div>
    </Dialog>
  );
}
