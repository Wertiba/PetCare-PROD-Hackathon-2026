'use client';

import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from 'motion/react';

const AUTO_HIDE_S = 5;

const formatTime = (value: number) =>
  new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value * 1000));

export function NextReminderToast({
  next,
  onUndo,
  onClose,
}: {
  next: { id: string; time: number } | null;
  onUndo: () => void;
  onClose: () => void;
}) {
  const reduced = useReducedMotion();

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed top-36 left-1/2 z-40 w-[calc(100vw-2rem)] max-w-72 -translate-x-1/2"
    >
      <AnimatePresence>
        {next && (
          <motion.div
            key={next.id}
            role="status"
            initial={
              reduced ? false : { opacity: 0, y: -12 }
            }
            animate={{ opacity: 1, y: 0 }}
            exit={
              reduced ? undefined : { opacity: 0, y: -12 }
            }
            className="pointer-events-auto overflow-hidden rounded-md bg-[var(--forest)] text-white shadow-[3px_3px_0_var(--lime)]"
          >
            <div className="flex items-center justify-between gap-3 px-3 py-2.5">
              <p className="min-w-0 text-sm font-bold">
                Следующее напоминание —{' '}
                {formatTime(next.time)}
              </p>
              <button
                type="button"
                onClick={onUndo}
                className="shrink-0 rounded-sm bg-[var(--lime)] px-2.5 py-1 text-xs font-bold text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Отменить
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
  );
}
