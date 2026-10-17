export const THEME_STORAGE_KEY = 'petcare-theme';
const THEME_CHANGE_EVENT = 'petcare-theme-change';

export type Theme = 'dark' | 'light';

export const getStoredTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light';

  return window.localStorage.getItem(THEME_STORAGE_KEY) ===
    'dark'
    ? 'dark'
    : 'light';
};

export const applyTheme = (theme: Theme) => {
  document.documentElement.dataset.theme = theme;
  window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
};

export const subscribeToTheme = (onChange: () => void) => {
  window.addEventListener(THEME_CHANGE_EVENT, onChange);
  return () =>
    window.removeEventListener(
      THEME_CHANGE_EVENT,
      onChange,
    );
};
