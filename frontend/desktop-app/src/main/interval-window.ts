import { BrowserWindow, app } from 'electron';

import {
  harden,
  loadPage,
  preloadPath,
} from './window-utils';

let intervalWindow: BrowserWindow | null = null;

export const getIntervalWindow = () => intervalWindow;

export function openIntervalWindow() {
  if (intervalWindow) {
    intervalWindow.show();
    intervalWindow.focus();
    return;
  }
  const window = new BrowserWindow({
    width: 360,
    height: 300,
    resizable: false,
    fullscreenable: false,
    minimizable: false,
    maximizable: false,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: preloadPath('interval'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  intervalWindow = window;
  harden(window);
  window.once('ready-to-show', () => {
    window.show();
    // The app has no Dock icon, so bring the window forward explicitly.
    app.focus({ steal: true });
  });
  window.on('closed', () => {
    intervalWindow = null;
  });
  loadPage(window, 'interval');
}

export function closeIntervalWindow() {
  intervalWindow?.close();
}
