/**
 * API бэка. Тот же адрес, что NEXT_PUBLIC_API_BASE_URL в frontend/.env:
 * прокси :3000/api/v1 из next.config ведёт на :8080, где локального бэка нет.
 * PETCARE_API_URL переопределяет адрес (локальный бэк, мок для проверки).
 */
export const API_URL =
  process.env.PETCARE_API_URL ??
  'https://hack-led-15-vm1-3f8c4e.vmaas-spirit.t-education.com/api/v1';

export const REQUEST_TIMEOUT_MS = 15_000;

export const POLL_MINUTES_OPTIONS = [1, 5, 10, 15] as const;
export const DEFAULT_POLL_MINUTES = 10;
/** Повтор опроса после сетевой ошибки, в том числе сразу после пробуждения. */
export const RETRY_DELAY_MS = 30_000;
export const SNOOZE_MINUTES = 10;
