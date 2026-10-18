import { join } from 'node:path';

import { Menu, Tray, app, nativeImage } from 'electron';

import {
  SPRITE_ANIMALS,
  type SpriteAnimal,
} from '../shared/config';
import { POLL_MINUTES_OPTIONS } from './config';
import { getSettings } from './settings';

interface TrayActions {
  isSignedIn: () => boolean;
  openLogin: () => void;
  signOut: () => void;
  openApp: () => void;
  checkNow: () => void;
  setDnd: (dnd: boolean) => void;
  setPollMinutes: (minutes: number) => void;
  openIntervalWindow: () => void;
  setSpriteAnimal: (animal: SpriteAnimal | null) => void;
}

export function createTray(actions: TrayActions) {
  const icon = nativeImage.createFromPath(
    join(app.getAppPath(), 'resources', 'trayTemplate.png'),
  );
  icon.setTemplateImage(true);
  const tray = new Tray(icon);
  tray.setToolTip('petcare');

  function refresh() {
    const { dnd, pollMinutes, spriteAnimal } =
      getSettings();
    const signedIn = actions.isSignedIn();
    const isPreset = (
      POLL_MINUTES_OPTIONS as readonly number[]
    ).includes(pollMinutes);
    tray.setContextMenu(
      Menu.buildFromTemplate([
        signedIn
          ? {
              label: 'Открыть petcare',
              click: actions.openApp,
            }
          : { label: 'Войти…', click: actions.openLogin },
        ...(signedIn
          ? [
              {
                label: 'Проверить напоминания сейчас',
                click: actions.checkNow,
              },
            ]
          : []),
        { type: 'separator' },
        {
          label: 'Не беспокоить',
          type: 'checkbox',
          checked: dnd,
          click: (item) => actions.setDnd(item.checked),
        },
        {
          label: 'Картинка питомца',
          submenu: [
            {
              label: 'Как в petcare',
              type: 'radio' as const,
              checked: spriteAnimal === null,
              click: () => actions.setSpriteAnimal(null),
            },
            ...SPRITE_ANIMALS.map((animal) => ({
              label: animal,
              type: 'radio' as const,
              checked: spriteAnimal === animal,
              click: () => actions.setSpriteAnimal(animal),
            })),
          ],
        },
        {
          label: 'Проверять напоминания',
          submenu: [
            ...POLL_MINUTES_OPTIONS.map((minutes) => ({
              label: `Каждую${minutes === 1 ? '' : 'е'} ${minutes === 1 ? 'минуту' : `${minutes} мин`}`,
              type: 'radio' as const,
              checked: pollMinutes === minutes,
              click: () => actions.setPollMinutes(minutes),
            })),
            { type: 'separator' as const },
            {
              label: isPreset
                ? 'Свой интервал…'
                : `Свой: каждые ${pollMinutes} мин…`,
              type: 'radio' as const,
              checked: !isPreset,
              click: actions.openIntervalWindow,
            },
          ],
        },
        {
          label: app.isPackaged
            ? 'Запускать при входе в систему'
            : 'Запускать при входе (в собранной версии)',
          type: 'checkbox',
          // Registering the dev Electron binary as a login item is useless.
          enabled: app.isPackaged,
          checked: app.getLoginItemSettings().openAtLogin,
          click: (item) =>
            app.setLoginItemSettings({
              openAtLogin: item.checked,
            }),
        },
        { type: 'separator' },
        ...(signedIn
          ? [
              {
                label: 'Выйти из аккаунта',
                click: actions.signOut,
              },
            ]
          : []),
        { label: 'Закрыть питомца', role: 'quit' as const },
      ]),
    );
  }

  refresh();
  return { refresh };
}
