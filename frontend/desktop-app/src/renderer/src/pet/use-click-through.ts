import { useEffect } from 'react';

const HIT_SELECTOR = '[data-hit]';

/**
 * The pet window ignores the mouse except over elements marked `data-hit`.
 * mousemove keeps arriving while ignored (forwarded by the main process),
 * so the window becomes clickable only while the cursor is over the pet.
 */
export function useClickThrough() {
  useEffect(() => {
    let interactive = false;
    const set = (next: boolean) => {
      if (next === interactive) return;
      interactive = next;
      window.petApi.setInteractive(next);
    };
    const onMove = (event: MouseEvent) =>
      set(
        event.target instanceof Element &&
          event.target.closest(HIT_SELECTOR) !== null,
      );
    const onLeave = () => set(false);

    window.addEventListener('mousemove', onMove);
    document.documentElement.addEventListener(
      'mouseleave',
      onLeave,
    );
    return () => {
      window.removeEventListener('mousemove', onMove);
      document.documentElement.removeEventListener(
        'mouseleave',
        onLeave,
      );
    };
  }, []);
}
