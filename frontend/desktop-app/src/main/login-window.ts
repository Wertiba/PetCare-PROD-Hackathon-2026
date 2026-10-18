import { BrowserWindow, app } from 'electron';

import {
  harden,
  loadPage,
  preloadPath,
} from './window-utils';

let loginWindow: BrowserWindow | null = null;

export const getLoginWindow = () => loginWindow;

export function openLoginWindow() {
  if (loginWindow) {
    loginWindow.show();
    loginWindow.focus();
    return;
  }
  const window = new BrowserWindow({
    width: 480,
    height: 820,
    resizable: false,
    fullscreenable: false,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: preloadPath('login'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  loginWindow = window;
  harden(window);
  window.once('ready-to-show', () => {
    window.show();
    // The app has no Dock icon, so bring the window forward explicitly.
    app.focus({ steal: true });
  });
  window.on('closed', () => {
    loginWindow = null;
  });
  loadPage(window, 'login');
}

export function closeLoginWindow() {
  loginWindow?.close();
}
