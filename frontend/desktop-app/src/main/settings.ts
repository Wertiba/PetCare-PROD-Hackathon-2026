import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { app } from 'electron';

import type { SpriteAnimal } from '../shared/config';
import { DEFAULT_POLL_MINUTES } from './config';

interface Settings {
  pollMinutes: number;
  dnd: boolean;
  /** null — the picture follows the pet's species in petcare. */
  spriteAnimal: SpriteAnimal | null;
}

const DEFAULTS: Settings = {
  pollMinutes: DEFAULT_POLL_MINUTES,
  dnd: false,
  spriteAnimal: null,
};

let settings: Settings | null = null;

const settingsFile = () =>
  join(app.getPath('userData'), 'settings.json');

export function getSettings(): Settings {
  if (!settings) {
    try {
      settings = {
        ...DEFAULTS,
        ...(JSON.parse(
          readFileSync(settingsFile(), 'utf8'),
        ) as Partial<Settings>),
      };
    } catch {
      // First run or a broken file: start from defaults.
      settings = { ...DEFAULTS };
    }
  }
  return settings;
}

export function updateSettings(patch: Partial<Settings>) {
  settings = { ...getSettings(), ...patch };
  writeFileSync(
    settingsFile(),
    JSON.stringify(settings, null, 2),
  );
}
