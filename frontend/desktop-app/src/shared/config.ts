/** Основное приложение: сюда ведут «Открыть» и ссылка на регистрацию. */
export const APP_URL =
  'https://hack-led-15-vm1-3f8c4e.vmaas-spirit.t-education.com';

/**
 * Картинки питомца. «Кошка» и «Собака» совпадают с видами на бэке
 * (alembic 0006) и подбираются сами; остальные — только выбор в трее.
 */
export const SPRITE_ANIMALS = [
  'Кошка',
  'Собака',
  'Аксолотль',
] as const;
export type SpriteAnimal = (typeof SPRITE_ANIMALS)[number];

/** Границы интервала опроса в минутах (свой ввод в трее). */
export const POLL_MINUTES_MIN = 1;
export const POLL_MINUTES_MAX = 1440;
