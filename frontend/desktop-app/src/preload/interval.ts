import { contextBridge, ipcRenderer } from 'electron';

import type {
  IntervalApi,
  IpcChannel,
} from '../shared/ipc';

const channel = (name: IpcChannel) => name;

const api: IntervalApi = {
  getPollMinutes: () =>
    ipcRenderer.invoke(
      channel('interval:get'),
    ) as Promise<number>,
  savePollMinutes: (minutes) =>
    ipcRenderer.invoke(
      channel('interval:save'),
      minutes,
    ) as Promise<boolean>,
};

contextBridge.exposeInMainWorld('intervalApi', api);
