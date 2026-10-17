'use client';

import { useEffect, useRef } from 'react';

interface DialogProps {
  children: React.ReactNode;
  isDismissable?: boolean;
  labelledBy: string;
  onClose: () => void;
}

/** A small shared dialog primitive for feature-owned dialog content. */
export function Dialog({
  children,
  isDismissable = true,
  labelledBy,
  onClose,
}: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const previouslyFocused =
      document.activeElement as HTMLElement | null;
    const dialog = dialogRef.current;
    const firstFocusable =
      dialog?.querySelector<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
    firstFocusable?.focus();

    const closeOnEscape = (event: KeyboardEvent) => {
      if (isDismissable && event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', closeOnEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener(
        'keydown',
        closeOnEscape,
      );
      document.body.style.overflow = '';
      previouslyFocused?.focus();
    };
  }, [isDismissable, onClose]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-[var(--forest)]/45 p-4"
      onPointerDown={(event) => {
        if (
          isDismissable &&
          event.target === event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        className="max-h-[calc(100dvh-2rem)] w-full overflow-y-auto rounded-md border-2 border-[var(--forest)] bg-[var(--cream)] shadow-[6px_6px_0_var(--forest)]"
      >
        {children}
      </div>
    </div>
  );
}
