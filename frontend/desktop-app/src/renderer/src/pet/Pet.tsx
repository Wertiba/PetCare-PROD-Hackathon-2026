import { useEffect, useState } from 'react';

import type { PetState } from '../../../shared/ipc';
import { spriteFor } from './sprites';
import { useClickThrough } from './use-click-through';

const formatTime = (value: number) =>
  new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value * 1000));

// Стили кнопок — как в frontend/src/widgets/ui/ReminderToast.tsx
const actionButtonClassName =
  'rounded-sm border px-2.5 py-1 text-xs font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50';

export function Pet() {
  const [state, setState] = useState<PetState | null>(null);
  // In «do not disturb» the bubble stays closed until the pet is clicked.
  const [peek, setPeek] = useState(false);

  useClickThrough();

  useEffect(() => {
    let active = true;
    void window.petApi.getState().then((initial) => {
      if (active) setState(initial);
    });
    const unsubscribe = window.petApi.onState(setState);
    return () => {
      active = false;
      unsubscribe();
    };
  }, []);

  if (!state) return null;

  const alert = state.signedIn
    ? state.alerts[0]
    : undefined;
  const moreCount = state.alerts.length - 1;
  const showBubble = Boolean(alert) && (!state.dnd || peek);
  const calling = Boolean(alert) && !state.dnd;

  const sprite = spriteFor(
    state.spriteAnimal ??
      alert?.animalName ??
      state.homeAnimalName,
  );
  // Не вошли — питомец спит, клик открывает вход.
  const onPetClick = () => {
    if (!state.signedIn) window.petApi.openLogin();
    else if (alert) setPeek((value) => !value);
  };
  const petLabel = !state.signedIn
    ? 'Войти в petcare'
    : alert
      ? 'Питомец зовёт'
      : 'Питомец спит';

  return (
    <main className="fixed inset-0 flex flex-col items-end justify-end gap-3 p-2">
      {showBubble && alert ? (
        <section
          data-hit
          role="status"
          aria-live="polite"
          className="w-72 rounded-md border border-[var(--forest)]/25 bg-white px-3 py-2.5 shadow-[3px_3px_0_var(--forest)]"
        >
          <div className="flex items-center justify-between gap-2">
            <p className="text-[11px] font-bold tracking-[.12em] text-[var(--forest)]/60 uppercase">
              Напоминание
            </p>
            <div className="flex items-center gap-1.5">
              {moreCount > 0 && (
                <span className="text-xs text-[var(--forest)]/60">
                  ещё {moreCount}
                </span>
              )}
              <button
                type="button"
                aria-label="Скрыть напоминание"
                onClick={() =>
                  window.petApi.dismissAlert(alert.key)
                }
                className="size-5 shrink-0 rounded-sm leading-none text-[var(--forest)]/60 hover:text-[var(--forest)] focus-visible:outline-2 focus-visible:outline-[var(--forest)]"
              >
                ×
              </button>
            </div>
          </div>
          <p className="mt-1 truncate text-sm font-black text-[var(--forest)]">
            {alert.eventName}
          </p>
          <p className="text-xs text-[var(--ink)]/60">
            {formatTime(alert.time)}
          </p>
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={() =>
                window.petApi.openAlert(alert.key)
              }
              className={`${actionButtonClassName} border-[var(--forest)] bg-[var(--forest)] text-white hover:bg-[var(--forest)]/90`}
            >
              Открыть
            </button>
            <button
              type="button"
              onClick={() =>
                window.petApi.snoozeAlert(alert.key)
              }
              className={`${actionButtonClassName} border-[var(--forest)]/25 bg-white text-[var(--forest)] hover:border-[var(--forest)]`}
            >
              Отложить
            </button>
          </div>
        </section>
      ) : null}

      <button
        data-hit
        type="button"
        onClick={onPetClick}
        aria-label={petLabel}
        className={
          calling ? 'motion-safe:animate-bounce' : undefined
        }
      >
        <img
          src={alert ? sprite.awake : sprite.sleeping}
          alt=""
          draggable={false}
          className="size-24 [image-rendering:pixelated]"
        />
      </button>
    </main>
  );
}
