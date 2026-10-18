import { contextBridge, ipcRenderer } from 'electron';

import type {
  IpcChannel,
  PetApi,
  PetState,
} from '../shared/ipc';

const channel = (name: IpcChannel) => name;

const api: PetApi = {
  getState: () =>
    ipcRenderer.invoke(
      channel('pet:get-state'),
    ) as Promise<PetState>,
  onState: (listener) => {
    const handler = (
      _event: Electron.IpcRendererEvent,
      state: PetState,
    ) => listener(state);
    ipcRenderer.on(channel('pet:state'), handler);
    return () => {
      ipcRenderer.removeListener(
        channel('pet:state'),
        handler,
      );
    };
  },
  setInteractive: (interactive) =>
    ipcRenderer.send(
      channel('pet:set-interactive'),
      interactive,
    ),
  openLogin: () =>
    ipcRenderer.send(channel('pet:open-login')),
  openAlert: (key) =>
    ipcRenderer.send(channel('pet:open-alert'), key),
  snoozeAlert: (key) =>
    ipcRenderer.send(channel('pet:snooze-alert'), key),
  dismissAlert: (key) =>
    ipcRenderer.send(channel('pet:dismiss-alert'), key),
};

contextBridge.exposeInMainWorld('petApi', api);
