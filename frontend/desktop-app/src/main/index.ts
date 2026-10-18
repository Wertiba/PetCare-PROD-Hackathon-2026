import {
  type IpcMainEvent,
  type IpcMainInvokeEvent,
  app,
  ipcMain,
  shell,
} from 'electron';

import {
  APP_URL,
  POLL_MINUTES_MAX,
  POLL_MINUTES_MIN,
} from '../shared/config';
import type {
  IpcChannel,
  PetAlert,
  PetState,
} from '../shared/ipc';
import type { LoginDto } from '../shared/login.dto';
import type { Notification } from '../shared/notification.types';
import { createAlerts } from './alerts';
import {
  ApiError,
  fetchAnimalById,
  fetchNotificationById,
  fetchNotifications,
  fetchPetById,
  fetchPets,
} from './api';
import {
  closeIntervalWindow,
  getIntervalWindow,
  openIntervalWindow,
} from './interval-window';
import {
  closeLoginWindow,
  getLoginWindow,
  openLoginWindow,
} from './login-window';
import {
  createPetWindow,
  setPetInteractive,
} from './pet-window';
import {
  createScheduler,
  notificationKey,
} from './scheduler';
import {
  authorized,
  isSignedIn,
  restoreSession,
  setOnSessionExpired,
  signIn,
  signOut,
} from './session';
import { getSettings, updateSettings } from './settings';
import { createTray } from './tray';

const PAGE_SIZE = 100;
const MAX_PAGES = 10;

/** The pet calls about every pending reminder, whatever its type. */
const isPetReminder = (notification: Notification) =>
  notification.status === 'pending';

/**
 * All pending reminders: the API has no time filter and lists the latest
 * first, so page through and let the scheduler pick the next 24 hours.
 */
async function fetchReminders(): Promise<Notification[]> {
  const items: Notification[] = [];
  for (let page = 0; page < MAX_PAGES; page++) {
    const result = await authorized((token) =>
      fetchNotifications(token, {
        page,
        size: PAGE_SIZE,
        status: 'pending',
      }),
    );
    items.push(...result.items);
    if (
      !result.items.length ||
      items.length >= result.total
    ) {
      break;
    }
  }
  return items.filter(isPetReminder);
}

async function confirmReminder(
  notification: Notification,
): Promise<Notification | null> {
  try {
    const current = await authorized((token) =>
      fetchNotificationById(token, notification.id),
    );
    // Confirmed or declined in the browser meanwhile: stay silent.
    return isPetReminder(current) ? current : null;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    // Offline right after wake: better to call than to miss it.
    console.warn(
      '[scheduler] cannot re-check reminder',
      error,
    );
    return notification;
  }
}

/** Animal name per pet: a pet's species does not change during a session. */
const animalNames = new Map<
  string,
  Promise<string | null>
>();

/** Pet → its animal id → the animal's name (GET /pets/{id}, /animals/{id}). */
function resolveAnimalName(petId: string) {
  let name = animalNames.get(petId);
  if (!name) {
    name = (async () => {
      const pet = await authorized((token) =>
        fetchPetById(token, petId),
      );
      if (!pet.animal) return null;
      const animalId = pet.animal.id;
      const animal = await authorized((token) =>
        fetchAnimalById(token, animalId),
      );
      return animal.name;
    })().catch((error: unknown) => {
      // Not cached: the next poll tries again.
      animalNames.delete(petId);
      console.warn('[pet] cannot resolve animal', error);
      return null;
    });
    animalNames.set(petId, name);
  }
  return name;
}

const toAlert = async (
  notification: Notification,
): Promise<PetAlert> => ({
  key: notificationKey(notification),
  notificationId: notification.id,
  eventId: notification.eventId,
  eventName: notification.eventName,
  time: notification.time,
  animalName: await resolveAnimalName(notification.petId),
});

/** Species of the user's first pet — the one asleep while nothing is due. */
async function fetchHomeAnimalName(): Promise<
  string | null | undefined
> {
  try {
    const { items } = await authorized((token) =>
      fetchPets(token, { page: 0, size: 1 }),
    );
    return items[0] ? resolveAnimalName(items[0].id) : null;
  } catch (error) {
    console.warn('[pet] cannot load pets', error);
    // Unknown: keep whatever was shown before.
    return undefined;
  }
}

const isPollMinutes = (value: unknown): value is number =>
  Number.isInteger(value) &&
  (value as number) >= POLL_MINUTES_MIN &&
  (value as number) <= POLL_MINUTES_MAX;

const isLoginDto = (value: unknown): value is LoginDto =>
  typeof value === 'object' &&
  value !== null &&
  typeof (value as LoginDto).login === 'string' &&
  typeof (value as LoginDto).password === 'string';

const on = (
  channel: IpcChannel,
  listener: (
    event: IpcMainEvent,
    ...args: unknown[]
  ) => void,
) => ipcMain.on(channel, listener);

const handle = (
  channel: IpcChannel,
  listener: (
    event: IpcMainInvokeEvent,
    ...args: unknown[]
  ) => unknown,
) => ipcMain.handle(channel, listener);

function start() {
  app.dock?.hide();

  const pet = createPetWindow();
  const openApp = () =>
    void shell.openExternal(`${APP_URL}/dashboard`);

  let homeAnimalName: string | null = null;

  const state = (): PetState => ({
    signedIn: isSignedIn(),
    homeAnimalName,
    dnd: getSettings().dnd,
    spriteAnimal: getSettings().spriteAnimal,
    alerts: alerts.list(),
  });
  const broadcast = () => {
    if (!pet.isDestroyed()) {
      pet.webContents.send(
        'pet:state' satisfies IpcChannel,
        state(),
      );
    }
    tray.refresh();
  };

  const alerts = createAlerts({
    isDnd: () => getSettings().dnd,
    onChange: broadcast,
    onOpen: openApp,
  });

  const scheduler = createScheduler({
    fetchNotifications: fetchReminders,
    confirm: confirmReminder,
    onFire: (notification) =>
      void toAlert(notification).then(alerts.add),
    onSynced: (notifications) => {
      void Promise.all(
        notifications
          .filter((item) => item.time * 1000 <= Date.now())
          .map(toAlert),
      ).then(alerts.reconcile);
      void fetchHomeAnimalName().then((name) => {
        if (name === undefined || name === homeAnimalName) {
          return;
        }
        homeAnimalName = name;
        broadcast();
      });
    },
    pollMs: () => getSettings().pollMinutes * 60_000,
  });

  const onSignedIn = () => {
    scheduler.start();
    broadcast();
  };
  const onSignedOut = () => {
    scheduler.stop();
    alerts.clear();
    animalNames.clear();
    homeAnimalName = null;
    broadcast();
  };

  const tray = createTray({
    isSignedIn,
    openLogin: openLoginWindow,
    signOut: () => {
      onSignedOut();
      void signOut().then(broadcast);
    },
    openApp,
    checkNow: () => scheduler.resync(),
    setDnd: (dnd) => {
      updateSettings({ dnd });
      broadcast();
    },
    setSpriteAnimal: (spriteAnimal) => {
      updateSettings({ spriteAnimal });
      broadcast();
    },
    setPollMinutes: (pollMinutes) =>
      setPollMinutes(pollMinutes),
    openIntervalWindow: () => {
      openIntervalWindow();
      // The radio item checks itself on click; until the user saves,
      // the menu must keep showing the current interval.
      tray.refresh();
    },
  });

  function setPollMinutes(pollMinutes: number) {
    updateSettings({ pollMinutes });
    scheduler.resync();
    tray.refresh();
  }

  setOnSessionExpired(onSignedOut);

  const fromPet = (
    event: IpcMainEvent | IpcMainInvokeEvent,
  ) => event.sender === pet.webContents;

  handle('pet:get-state', (event) =>
    fromPet(event) ? state() : null,
  );
  on('pet:set-interactive', (event, interactive) => {
    if (
      fromPet(event) &&
      typeof interactive === 'boolean'
    ) {
      setPetInteractive(pet, interactive);
    }
  });
  on('pet:open-login', (event) => {
    if (fromPet(event)) openLoginWindow();
  });
  on('pet:open-alert', (event, key) => {
    if (fromPet(event) && typeof key === 'string') {
      alerts.open(key);
    }
  });
  on('pet:snooze-alert', (event, key) => {
    if (fromPet(event) && typeof key === 'string') {
      alerts.snooze(key);
    }
  });
  on('pet:dismiss-alert', (event, key) => {
    if (fromPet(event) && typeof key === 'string') {
      alerts.dismiss(key);
    }
  });
  handle('login:submit', async (event, values) => {
    const loginWindow = getLoginWindow();
    if (
      !loginWindow ||
      event.sender !== loginWindow.webContents ||
      !isLoginDto(values)
    ) {
      return false;
    }
    try {
      await signIn(values);
    } catch (error) {
      console.warn('[session] login failed', error);
      return false;
    }
    closeLoginWindow();
    onSignedIn();
    return true;
  });

  const fromIntervalWindow = (event: IpcMainInvokeEvent) =>
    event.sender === getIntervalWindow()?.webContents;

  handle('interval:get', (event) =>
    fromIntervalWindow(event)
      ? getSettings().pollMinutes
      : null,
  );
  handle('interval:save', (event, minutes) => {
    if (
      !fromIntervalWindow(event) ||
      !isPollMinutes(minutes)
    ) {
      return false;
    }
    setPollMinutes(minutes);
    closeIntervalWindow();
    return true;
  });

  if (restoreSession()) {
    onSignedIn();
  } else {
    openLoginWindow();
  }
}

if (app.requestSingleInstanceLock()) {
  void app.whenReady().then(start);
} else {
  app.quit();
}
