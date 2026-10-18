/// <reference types="vite/client" />
import type {
  IntervalApi,
  LoginApi,
  PetApi,
} from '../../shared/ipc';

declare global {
  interface Window {
    petApi: PetApi;
    loginApi: LoginApi;
    intervalApi: IntervalApi;
  }
}
