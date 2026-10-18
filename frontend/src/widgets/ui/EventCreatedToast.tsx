'use client';

import type { Event } from '@src/entities/event';
import { CreateNotificationForm } from '@src/features/notification/create-notification';
import { Dialog } from '@src/shared/ui';
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from 'motion/react';
import { useState } from 'react';

const AUTO_HIDE_S = 5;
const DEFAULT_HOUR = 9;

const dayFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
});

export function EventCreatedToast({
  event,
  onClose,
}: {
  event: Event | null;
  onClose: () => void;
}) {
  const reduced = useReducedMotion();
  const [dialogEvent, setDialogEvent] =
    useState<Event | null>(null);
  const canRemind = event?.status === 'planned';

  const defaultTime = dialogEvent
    ? new Date(dialogEvent.schedule * 1000).setHours(
        DEFAULT_HOUR,
        0,
        0,
        0,
      ) / 1000
    : undefined;

  return (
    <>
      <div
        aria-live="polite"
        className="pointer-events-none fixed right-4 bottom-36 z-40 w-[calc(100vw-2rem)] max-w-72"
      >
        <AnimatePresence>
          {event && canRemind && (
            <motion.div
              key={event.id}
              role="status"
              initial={
                reduced ? false : { opacity: 0, y: 12 }
              }
              animate={{ opacity: 1, y: 0 }}
              exit={
                reduced ? undefined : { opacity: 0, y: 12 }
              }
              className="pointer-events-auto overflow-hidden rounded-md bg-[var(--forest)] text-white shadow-[3px_3px_0_var(--lime)]"
            >
              <div className="px-3 py-2.5">
                <div className="flex items-start justify-between gap-2">
                  <p className="min-w-0 text-sm font-bold">
                    «{event.name}» создано
                  </p>
                  <button
                    type="button"
                    aria-label="Закрыть"
                    onClick={onClose}
                    className="size-5 shrink-0 rounded-sm leading-none text-white/70 hover:text-white focus-visible:outline-2 focus-visible:outline-white"
                  >
                    ×
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setDialogEvent(event);
                    onClose();
                  }}
                  className="mt-2 rounded-sm bg-[var(--lime)] px-2.5 py-1 text-xs font-bold text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
                >
                  Создать уведомление на{' '}
                  {dayFormatter.format(
                    new Date(event.schedule * 1000),
                  )}
                </button>
              </div>
              <motion.div
                aria-hidden="true"
                className="h-1 origin-left bg-[var(--lime)]"
                initial={{ scaleX: 1 }}
                animate={{ scaleX: 0 }}
                transition={{
                  duration: AUTO_HIDE_S,
                  ease: 'linear',
                }}
                onAnimationComplete={onClose}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {dialogEvent ? (
        <Dialog
          labelledBy="event-created-notification-title"
          onClose={() => setDialogEvent(null)}
        >
          <div className="mx-auto w-xl max-w-full p-5 sm:p-6">
            <div className="border-b border-[var(--forest)]/15 pb-4">
              <p className="text-sm font-semibold text-[var(--ink)]/55">
                {dialogEvent.name}
              </p>
              <h2
                id="event-created-notification-title"
                className="mt-1 text-2xl font-black text-[var(--forest)]"
              >
                Новое уведомление
              </h2>
            </div>
            <div className="mt-5">
              <CreateNotificationForm
                eventId={dialogEvent.id}
                defaultTime={defaultTime}
                onCancel={() => setDialogEvent(null)}
                onSuccess={() => setDialogEvent(null)}
              />
            </div>
          </div>
        </Dialog>
      ) : null}
    </>
  );
}
