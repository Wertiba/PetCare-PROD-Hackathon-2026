import { join } from 'node:path';

import { type BrowserWindow, app, shell } from 'electron';

import { APP_URL } from '../shared/config';

type Page = 'pet' | 'login' | 'interval';

export const preloadPath = (page: Page) =>
  join(__dirname, `../preload/${page}.js`);

export function loadPage(
  window: BrowserWindow,
  page: Page,
) {
  const devUrl = process.env.ELECTRON_RENDERER_URL;
  if (!app.isPackaged && devUrl) {
    void window.loadURL(`${devUrl}/${page}.html`);
  } else {
    void window.loadFile(
      join(__dirname, `../renderer/${page}.html`),
    );
  }
}

/** Keeps the window on its own page; links to the app open in the browser. */
export function harden(window: BrowserWindow) {
  window.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith(`${APP_URL}/`)) {
      void shell.openExternal(url);
    }
    return { action: 'deny' };
  });
  window.webContents.on('will-navigate', (event) =>
    event.preventDefault(),
  );
}
