import { Notification } from 'electron';

import type { PetAlert } from '../shared/ipc';
import { SNOOZE_MINUTES } from './config';

const formatTime = (value: number) =>
  new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value * 1000));

const newestFirst = (a: PetAlert, b: PetAlert) =>
  b.time - a.time;

interface AlertsDeps {
  isDnd: () => boolean;
  onChange: () => void;
  onOpen: () => void;
}

/**
 * Due reminders the pet is calling about, newest first — like the toast in
 * the web app, they stay until confirmed in the browser or hidden here.
 */
export function createAlerts(deps: AlertsDeps) {
  let alerts: PetAlert[] = [];
  // Hidden locally (opened or dismissed), as `hiddenIds` in ReminderToast.
  const hidden = new Set<string>();
  const snoozes = new Map<string, NodeJS.Timeout>();
  // Notifications are kept referenced so their click handlers survive GC.
  const notifications = new Set<Notification>();

  function notify(alert: PetAlert) {
    if (deps.isDnd() || !Notification.isSupported()) return;
    const notification = new Notification({
      title: alert.eventName,
      body: `Напоминание на ${formatTime(alert.time)}`,
    });
    notifications.add(notification);
    notification.on('click', () => open(alert.key));
    notification.on('close', () =>
      notifications.delete(notification),
    );
    notification.show();
  }

  function remove(key: string) {
    const next = alerts.filter((item) => item.key !== key);
    if (next.length === alerts.length) return false;
    alerts = next;
    deps.onChange();
    return true;
  }

  /** A reminder that has just come due: calls with a system notification. */
  function add(alert: PetAlert) {
    if (
      hidden.has(alert.key) ||
      alerts.some((item) => item.key === alert.key)
    ) {
      return;
    }
    alerts = [...alerts, alert].sort(newestFirst);
    notify(alert);
    deps.onChange();
  }

  /**
   * Mirrors the backend's due list: adds reminders that came due earlier
   * (quietly, without a system notification) and drops the ones already
   * confirmed or declined in the browser.
   */
  function reconcile(due: PetAlert[]) {
    const dueKeys = new Set(due.map((item) => item.key));
    const kept = alerts.filter((item) =>
      dueKeys.has(item.key),
    );
    const keptKeys = new Set(kept.map((item) => item.key));
    const added = due.filter(
      (item) =>
        !keptKeys.has(item.key) &&
        !hidden.has(item.key) &&
        !snoozes.has(item.key),
    );
    if (kept.length === alerts.length && !added.length)
      return;
    alerts = [...kept, ...added].sort(newestFirst);
    deps.onChange();
  }

  function hide(key: string) {
    hidden.add(key);
    remove(key);
  }

  function open(key: string) {
    hide(key);
    deps.onOpen();
  }

  function snooze(key: string) {
    const alert = alerts.find((item) => item.key === key);
    if (!alert || !remove(key)) return;
    snoozes.set(
      key,
      setTimeout(() => {
        snoozes.delete(key);
        add(alert);
      }, SNOOZE_MINUTES * 60_000),
    );
  }

  function clear() {
    for (const timer of snoozes.values())
      clearTimeout(timer);
    snoozes.clear();
    hidden.clear();
    alerts = [];
    deps.onChange();
  }

  return {
    list: () => alerts,
    add,
    reconcile,
    open,
    snooze,
    dismiss: hide,
    clear,
  };
}
