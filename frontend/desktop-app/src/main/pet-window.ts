import { BrowserWindow, screen } from 'electron';

import {
  harden,
  loadPage,
  preloadPath,
} from './window-utils';

const WIDTH = 320;
const HEIGHT = 300;
const MARGIN = 16;

/** Bottom-right corner of the primary display, above the Dock / taskbar. */
function bounds() {
  const { workArea } = screen.getPrimaryDisplay();
  return {
    width: WIDTH,
    height: HEIGHT,
    x: workArea.x + workArea.width - WIDTH - MARGIN,
    y: workArea.y + workArea.height - HEIGHT - MARGIN,
  };
}

export function createPetWindow() {
  const window = new BrowserWindow({
    ...bounds(),
    show: false,
    frame: false,
    transparent: true,
    hasShadow: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: false,
    acceptFirstMouse: true,
    // NSPanel: floats over full-screen apps without activating the app.
    ...(process.platform === 'darwin'
      ? { type: 'panel' }
      : {}),
    webPreferences: {
      preload: preloadPath('pet'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  window.setAlwaysOnTop(true, 'screen-saver');
  window.setVisibleOnAllWorkspaces(true, {
    visibleOnFullScreen: true,
  });
  // Clicks pass through everywhere until the renderer reports the cursor
  // is over the pet itself; `forward` keeps mousemove coming for that.
  window.setIgnoreMouseEvents(true, { forward: true });
  harden(window);

  const place = () => {
    if (!window.isDestroyed()) window.setBounds(bounds());
  };
  screen.on('display-metrics-changed', place);
  screen.on('display-added', place);
  screen.on('display-removed', place);

  window.once('ready-to-show', () => window.showInactive());
  loadPage(window, 'pet');
  return window;
}

export function setPetInteractive(
  window: BrowserWindow,
  interactive: boolean,
) {
  window.setIgnoreMouseEvents(!interactive, {
    forward: true,
  });
}
