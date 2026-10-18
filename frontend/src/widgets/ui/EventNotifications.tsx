'use client';

import type { Event } from '@src/entities/event';
import {
  type Notification,
  useGetNotificationsQuery,
} from '@src/entities/notification';
import { useDeleteNotificationMutation } from '@src/features/notification/delete-notification';
import { UpdateNotificationForm } from '@src/features/notification/update-notification';
import { Dialog } from '@src/shared/ui';
import { Fragment, useCallback, useState } from 'react';

const dateTimeFormatter = new Intl.DateTimeFormat('ru-RU', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

const typeLabels: Record<Notification['type'], string> = {
  app: 'В приложении',
  telegram: 'Telegram',
  web_push: 'Push в браузере',
};

const statusLabels: Record<Notification['status'], string> =
  {
    pending: 'Ожидает',
    sent: 'Отправлено',
    read: 'Подтверждено',
    failed: 'Отклонено',
  };

const secondaryButtonClassName =
  'rounded-sm border border-[var(--forest)]/25 bg-white px-3 py-1.5 text-sm font-bold text-[var(--forest)] transition-colors hover:border-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50';

const isActive = (item: Notification) =>
  item.status === 'pending' || item.status === 'sent';

const reminderPlural = new Intl.PluralRules('ru-RU');
export const reminderWord = (count: number) => {
  const category = reminderPlural.select(count);
  return category === 'one'
    ? 'напоминание'
    : category === 'few'
      ? 'напоминания'
      : 'напоминаний';
};

export function EventReminderCount({
  event,
  onOpen,
}: {
  event: Event;
  onOpen: (event: Event) => void;
}) {
  const { data } = useGetNotificationsQuery({
    page: 0,
    size: 1,
    eventId: event.id,
  });
  const total = data?.total ?? 0;

  if (!total) return null;

  return (
    <button
      type="button"
      onClick={() => onOpen(event)}
      className="mt-2 text-sm font-semibold text-[var(--forest)] underline underline-offset-2 hover:text-[var(--forest)]/75 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)]"
    >
      {total} {reminderWord(total)}
    </button>
  );
}

export function EventNotificationsButton({
  event,
}: {
  event: Event;
}) {
  const [isOpen, setOpen] = useState(false);
  const { data } = useGetNotificationsQuery({
    page: 0,
    size: 100,
    eventId: event.id,
  });
  const total =
    data?.items.filter((item) => isActive(item)).length ??
    0;
  const close = useCallback(() => setOpen(false), []);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={secondaryButtonClassName}
      >
        Посмотреть напоминания ({total})
      </button>
      {isOpen ? (
        <EventNotificationsDialog
          event={event}
          onClose={close}
        />
      ) : null}
    </>
  );
}

export function EventNotificationsDialog({
  event,
  onClose,
}: {
  event: Event;
  onClose: () => void;
}) {
  const [editingId, setEditingId] = useState<string | null>(
    null,
  );
  const [deletingId, setDeletingId] = useState<
    string | null
  >(null);
  const { data, isPending, isError } =
    useGetNotificationsQuery({
      page: 0,
      size: 100,
      eventId: event.id,
    });
  const deletion = useDeleteNotificationMutation();
  // Newest first; answered (read/failed) reminders go below the active ones.
  const items = [...(data?.items ?? [])].sort(
    (a, b) =>
      Number(isActive(b)) - Number(isActive(a)) ||
      b.time - a.time,
  );
  const activeCount = items.filter(isActive).length;

  return (
    <Dialog
      labelledBy="event-notifications-title"
      onClose={onClose}
    >
      <div className="mx-auto w-xl max-w-full p-5 sm:p-6">
        <div className="flex min-w-0 items-start justify-between gap-4 border-b border-[var(--forest)]/15 pb-4">
          <div className="min-w-0">
            <p className="break-words text-sm font-semibold text-[var(--ink)]/55">
              {event.name}
            </p>
            <h2
              id="event-notifications-title"
              className="mt-1 break-words text-2xl font-black text-[var(--forest)]"
            >
              Напоминания
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть"
            className="grid size-9 shrink-0 place-items-center rounded-full border border-[var(--forest)]/25 text-lg hover:bg-[var(--lime)]"
          >
            ×
          </button>
        </div>

        <div className="mt-5 space-y-3">
          {isPending ? (
            <p className="text-sm text-[var(--ink)]/60">
              Загружаем напоминания…
            </p>
          ) : null}
          {isError ? (
            <p
              role="alert"
              className="text-sm text-red-800"
            >
              Не удалось загрузить напоминания.
            </p>
          ) : null}
          {!isPending && !isError && !items.length ? (
            <p className="text-sm text-[var(--ink)]/60">
              Напоминаний пока нет.
            </p>
          ) : null}
          {items.map((item, index) => (
            <Fragment key={item.id}>
              {index === activeCount && activeCount > 0 ? (
                <p className="pt-2 text-xs font-bold tracking-[.12em] text-[var(--ink)]/45 uppercase">
                  Обработанные
                </p>
              ) : null}
              <article
                className={
                  isActive(item)
                    ? 'border-l-4 border-[var(--lime)] bg-[var(--cream)] px-3 py-3'
                    : 'border-l-4 border-[var(--forest)]/15 bg-transparent px-3 py-3 opacity-60'
                }
              >
                {editingId === item.id ? (
                  <div className="flex flex-col gap-3">
                    <UpdateNotificationForm
                      notification={item}
                      onSuccess={() => setEditingId(null)}
                    />
                    <button
                      type="button"
                      onClick={() => setEditingId(null)}
                      className={secondaryButtonClassName}
                    >
                      Отменить изменения
                    </button>
                  </div>
                ) : (
                  <>
                    <p className="font-bold text-[var(--forest)]">
                      {dateTimeFormatter.format(
                        new Date(item.time * 1000),
                      )}
                    </p>
                    <p className="mt-1 text-sm text-[var(--ink)]/60">
                      {typeLabels[item.type]} ·{' '}
                      <span
                        className={
                          isActive(item)
                            ? undefined
                            : `font-semibold underline underline-offset-2 ${item.status === 'read' ? 'text-green-800' : 'text-red-800'}`
                        }
                      >
                        {statusLabels[item.status]}
                      </span>
                    </p>
                    {deletingId === item.id ? (
                      <div className="mt-3">
                        <p className="text-sm font-semibold text-red-800">
                          Удалить это напоминание?
                        </p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <button
                            type="button"
                            disabled={deletion.isPending}
                            onClick={() =>
                              deletion.mutate(item.id, {
                                onSuccess: () =>
                                  setDeletingId(null),
                              })
                            }
                            className={`${secondaryButtonClassName} text-red-800`}
                          >
                            Да, удалить
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              setDeletingId(null)
                            }
                            className={
                              secondaryButtonClassName
                            }
                          >
                            Отмена
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setDeletingId(null);
                            setEditingId(item.id);
                          }}
                          className={
                            secondaryButtonClassName
                          }
                        >
                          Изменить
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            setDeletingId(item.id)
                          }
                          className={`${secondaryButtonClassName} text-red-800`}
                        >
                          Удалить
                        </button>
                      </div>
                    )}
                  </>
                )}
              </article>
            </Fragment>
          ))}
          {deletion.error ? (
            <p
              role="alert"
              className="text-sm text-red-800"
            >
              Не удалось удалить напоминание. Попробуйте ещё
              раз.
            </p>
          ) : null}
        </div>
      </div>
    </Dialog>
  );
}
