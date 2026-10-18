'use client';

import type { EventPeriod } from '@src/entities/event';
import { fetchEventById } from '@src/entities/event/api';
import {
  type Notification,
  type NotificationStatus,
  useGetNotificationsQuery,
} from '@src/entities/notification';
import { createNotification } from '@src/entities/notification/api';
import { useDeleteNotificationMutation } from '@src/features/notification/delete-notification';
import { useUpdateNotificationMutation } from '@src/features/notification/update-notification';
import { queryKeys } from '@src/shared/api/query-keys';
import { showReminderPush } from '@src/shared/lib/web-push';
import {
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from 'motion/react';
import { useEffect, useState } from 'react';

import { reminderWord } from './EventNotifications';
import { NextReminderToast } from './NextReminderToast';

const POLL_INTERVAL_MS = 15_000;

const periodDays: Partial<Record<EventPeriod, number>> = {
  daily: 1,
  weekly: 7,
};
const periodMonths: Partial<Record<EventPeriod, number>> = {
  monthly: 1,
  quarterly: 3,
  half_year: 6,
  yearly: 12,
};

const addPeriod = (time: number, period: EventPeriod) => {
  const date = new Date(time * 1000);
  date.setDate(date.getDate() + (periodDays[period] ?? 0));
  date.setMonth(
    date.getMonth() + (periodMonths[period] ?? 0),
  );
  return date.getTime() / 1000;
};

const formatTime = (value: number) =>
  new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value * 1000));

const actionButtonClassName =
  'rounded-sm border px-2.5 py-1 text-xs font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50';

export function ReminderToast() {
  const queryClient = useQueryClient();
  const reduced = useReducedMotion();
  const [hiddenIds, setHiddenIds] = useState<string[]>([]);
  const [next, setNext] = useState<Notification | null>(
    null,
  );
  const update = useUpdateNotificationMutation();
  const remove = useDeleteNotificationMutation();
  const scheduleNext = useMutation({
    mutationFn: async (current: Notification) => {
      const event = await fetchEventById(current.eventId);
      if (event.period === 'none') return null;
      return createNotification({
        eventId: current.eventId,
        type: current.type,
        status: 'pending',
        time: addPeriod(current.time, event.period),
      });
    },
    onSuccess: (created) => {
      if (created) {
        setNext(created);
        void queryClient.invalidateQueries({
          queryKey: queryKeys.notifications.all,
        });
      }
    },
  });
  const resolve = (
    current: Notification,
    status: NotificationStatus,
  ) =>
    update.mutate(
      { id: current.id, data: { status } },
      { onSuccess: () => scheduleNext.mutate(current) },
    );
  const { data } = useGetNotificationsQuery({
    page: 0,
    size: 20,
    status: 'pending',
    due: true,
  });

  useEffect(() => {
    const timer = setInterval(() => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.notifications.all,
      });
    }, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [queryClient]);

  const visible =
    data?.items.filter(
      (item) => !hiddenIds.includes(item.id),
    ) ?? [];
  const notification = visible[0];
  const moreCount = visible.length - 1;

  useEffect(() => {
    if (!notification || notification.type !== 'web_push') {
      return;
    }

    void showReminderPush({
      id: notification.id,
      title: notification.eventName,
      body: `Напоминание на ${formatTime(notification.time)}`,
    });
  }, [notification]);

  return (
    <>
      <div
        aria-live="polite"
        className="pointer-events-none fixed top-4 left-1/2 z-40 w-[calc(100vw-2rem)] max-w-72 -translate-x-1/2"
      >
        <AnimatePresence>
          {notification && (
            <motion.div
              key={notification.id}
              role="status"
              initial={
                reduced ? false : { opacity: 0, y: -12 }
              }
              animate={{ opacity: 1, y: 0 }}
              exit={
                reduced ? undefined : { opacity: 0, y: -12 }
              }
              className="pointer-events-auto rounded-md border border-[var(--forest)]/25 bg-white px-3 py-2.5 shadow-[3px_3px_0_var(--forest)]"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-[11px] font-bold tracking-[.12em] text-[var(--forest)]/60 uppercase">
                  Напоминание
                </p>
                <div className="flex items-center gap-1.5">
                  {moreCount > 0 && (
                    <span className="text-xs text-[var(--forest)]/60">
                      ещё {moreCount}{' '}
                      {reminderWord(moreCount)}
                    </span>
                  )}
                  <button
                    type="button"
                    aria-label="Скрыть напоминание"
                    onClick={() =>
                      setHiddenIds((ids) => [
                        ...ids,
                        notification.id,
                      ])
                    }
                    className="size-5 shrink-0 rounded-sm leading-none text-[var(--forest)]/60 hover:text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-[var(--forest)]"
                  >
                    ×
                  </button>
                </div>
              </div>
              <p className="mt-1 truncate text-sm font-black text-[var(--forest)]">
                {notification.eventName}
                <span className="ml-2 font-normal text-[var(--ink)]/60">
                  {formatTime(notification.time)}
                </span>
              </p>
              <div className="mt-2 flex gap-2">
                <button
                  type="button"
                  disabled={update.isPending}
                  onClick={() =>
                    resolve(notification, 'read')
                  }
                  className={`${actionButtonClassName} border-[var(--forest)] bg-[var(--forest)] text-white hover:bg-[var(--forest)]/90`}
                >
                  Подтвердить
                </button>
                <button
                  type="button"
                  disabled={update.isPending}
                  onClick={() =>
                    resolve(notification, 'failed')
                  }
                  className={`${actionButtonClassName} border-[var(--forest)]/25 bg-white text-[var(--forest)] hover:border-[var(--forest)]`}
                >
                  Отклонить
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <NextReminderToast
        next={next}
        onUndo={() => {
          if (next) remove.mutate(next.id);
          setNext(null);
        }}
        onClose={() => setNext(null)}
      />
    </>
  );
}
