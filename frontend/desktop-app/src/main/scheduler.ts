import { powerMonitor } from 'electron';

import type { Notification } from '../shared/notification.types';
import { RETRY_DELAY_MS } from './config';

const HORIZON_MS = 24 * 60 * 60 * 1000;

export const notificationKey = (
  notification: Notification,
) => `${notification.id}:${notification.time}`;

interface SchedulerDeps {
  fetchNotifications: () => Promise<Notification[]>;
  /** Re-reads the reminder right before it fires; null — it is no longer due. */
  confirm: (
    notification: Notification,
  ) => Promise<Notification | null>;
  onFire: (notification: Notification) => void;
  /** Fresh list after every successful poll. */
  onSynced: (notifications: Notification[]) => void;
  pollMs: () => number;
}

/**
 * Polls the backend for pending reminders and fires each one with a local
 * timer at its exact time. Node timers stall while the laptop sleeps, so on
 * wake the cached list is replayed first, then the backend is re-read.
 */
export function createScheduler(deps: SchedulerDeps) {
  let running = false;
  let notifications: Notification[] = [];
  /** Everything due at or before this moment has been handled. */
  let handledUntil = Date.now();
  const fired = new Set<string>();
  const timers = new Map<string, NodeJS.Timeout>();
  let pollTimer: NodeJS.Timeout | undefined;

  async function fire(notification: Notification) {
    const key = notificationKey(notification);
    if (!running || fired.has(key)) return;
    fired.add(key);
    clearTimeout(timers.get(key));
    timers.delete(key);
    const current = await deps.confirm(notification);
    if (
      running &&
      current &&
      notificationKey(current) === key
    ) {
      deps.onFire(current);
    }
  }

  function plan() {
    const now = Date.now();
    const keys = new Set(
      notifications.map(notificationKey),
    );
    for (const [key, timer] of timers) {
      if (!keys.has(key)) {
        clearTimeout(timer);
        timers.delete(key);
      }
    }
    for (const notification of notifications) {
      const key = notificationKey(notification);
      const at = notification.time * 1000;
      if (fired.has(key)) continue;
      if (at <= now) {
        // Came due since the last pass (a late timer, sleep); reminders
        // that were overdue before the pet started stay silent.
        if (at > handledUntil) void fire(notification);
        continue;
      }
      if (!timers.has(key) && at - now <= HORIZON_MS) {
        timers.set(
          key,
          setTimeout(
            () => void fire(notification),
            at - now,
          ),
        );
      }
    }
    handledUntil = now;
  }

  function schedulePoll(delayMs: number) {
    clearTimeout(pollTimer);
    if (running) {
      pollTimer = setTimeout(() => void sync(), delayMs);
    }
  }

  async function sync() {
    clearTimeout(pollTimer);
    try {
      const next = await deps.fetchNotifications();
      if (!running) return;
      notifications = next;
      plan();
      deps.onSynced(next);
      const pollMs = deps.pollMs();
      console.info(
        `[scheduler] ${next.length} pending reminder(s), ${timers.size} timer(s); next poll in ${pollMs / 60_000} min`,
      );
      schedulePoll(pollMs);
    } catch (error) {
      console.warn('[scheduler] sync failed', error);
      schedulePoll(RETRY_DELAY_MS);
    }
  }

  const onWake = () => {
    plan();
    void sync();
  };

  return {
    start() {
      if (running) return;
      running = true;
      handledUntil = Date.now();
      powerMonitor.on('resume', onWake);
      powerMonitor.on('unlock-screen', onWake);
      void sync();
    },
    stop() {
      running = false;
      clearTimeout(pollTimer);
      for (const timer of timers.values())
        clearTimeout(timer);
      timers.clear();
      notifications = [];
      powerMonitor.off('resume', onWake);
      powerMonitor.off('unlock-screen', onWake);
    },
    /** Re-reads the backend now: manual check, changed poll interval. */
    resync() {
      if (running) void sync();
    },
  };
}
