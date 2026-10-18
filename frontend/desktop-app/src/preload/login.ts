import { contextBridge, ipcRenderer } from 'electron';

import type { IpcChannel, LoginApi } from '../shared/ipc';

const channel = (name: IpcChannel) => name;

const api: LoginApi = {
  login: (values) =>
    ipcRenderer.invoke(
      channel('login:submit'),
      values,
    ) as Promise<boolean>,
};

contextBridge.exposeInMainWorld('loginApi', api);
