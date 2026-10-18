const SERVICE_WORKER_PATH = '/sw.js';
const shownReminderIds = new Set<string>();

export type WebPushPermissionResult =
  | { ok: true; registration: ServiceWorkerRegistration }
  | { ok: false; reason: string };

const isWebPushSupported = () =>
  typeof window !== 'undefined' &&
  'Notification' in window &&
  'serviceWorker' in navigator;

export async function ensureWebPushPermission(): Promise<WebPushPermissionResult> {
  if (!isWebPushSupported()) {
    return {
      ok: false,
      reason:
        'Этот браузер не поддерживает Push-уведомления.',
    };
  }

  const permission =
    Notification.permission === 'default'
      ? await Notification.requestPermission()
      : Notification.permission;

  if (permission !== 'granted') {
    return {
      ok: false,
      reason:
        permission === 'denied'
          ? 'Разрешите Push-уведомления в настройках браузера.'
          : 'Без разрешения браузера Push-уведомления не сработают.',
    };
  }

  try {
    const registration =
      await navigator.serviceWorker.register(
        SERVICE_WORKER_PATH,
        { scope: '/' },
      );
    return { ok: true, registration };
  } catch {
    return {
      ok: false,
      reason:
        'Не удалось включить Push-уведомления. Проверьте, что сайт открыт по HTTPS.',
    };
  }
}

export async function showReminderPush({
  body,
  id,
  title,
}: {
  body: string;
  id: string;
  title: string;
}) {
  if (
    !isWebPushSupported() ||
    Notification.permission !== 'granted'
  ) {
    return false;
  }
  if (shownReminderIds.has(id)) return true;

  try {
    const registration =
      await navigator.serviceWorker.register(
        SERVICE_WORKER_PATH,
        { scope: '/' },
      );
    const tag = `reminder-${id}`;
    const existing = await registration.getNotifications({
      tag,
    });
    if (existing.length) {
      shownReminderIds.add(id);
      return true;
    }

    await registration.showNotification(title, {
      body,
      data: { url: '/dashboard' },
      tag,
    });
    shownReminderIds.add(id);
    return true;
  } catch {
    return false;
  }
}
