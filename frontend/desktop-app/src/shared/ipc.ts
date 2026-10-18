import type { SpriteAnimal } from './config';
import type { Timestamp, Uid } from './global.types';
import type { LoginDto } from './login.dto';

/** Наступившее напоминание (любого type), о котором питомец зовёт. */
export interface PetAlert {
  /** `${notificationId}:${time}` — перенесённое напоминание получает новый ключ. */
  key: string;
  notificationId: Uid;
  eventId: Uid;
  eventName: string;
  time: Timestamp;
  /** Вид животного (GET /animals/{id}); потом по нему выберем спрайт. */
  animalName: string | null;
}

export interface PetState {
  signedIn: boolean;
  /** Вид первого питомца пользователя: он спит, пока напоминаний нет. */
  homeAnimalName: string | null;
  /** Картинка, выбранная в трее; null — по виду питомца из petcare. */
  spriteAnimal: SpriteAnimal | null;
  dnd: boolean;
  alerts: PetAlert[];
}

/** API окна питомца (preload/pet.ts → window.petApi). */
export interface PetApi {
  getState: () => Promise<PetState>;
  onState: (
    listener: (state: PetState) => void,
  ) => () => void;
  setInteractive: (interactive: boolean) => void;
  openLogin: () => void;
  openAlert: (key: string) => void;
  snoozeAlert: (key: string) => void;
  dismissAlert: (key: string) => void;
}

/** API окна входа (preload/login.ts → window.loginApi). */
export interface LoginApi {
  login: (values: LoginDto) => Promise<boolean>;
}

/** API окна своего интервала (preload/interval.ts → window.intervalApi). */
export interface IntervalApi {
  getPollMinutes: () => Promise<number>;
  savePollMinutes: (minutes: number) => Promise<boolean>;
}

export type IpcChannel =
  | 'pet:get-state'
  | 'pet:state'
  | 'pet:set-interactive'
  | 'pet:open-login'
  | 'pet:open-alert'
  | 'pet:snooze-alert'
  | 'pet:dismiss-alert'
  | 'login:submit'
  | 'interval:get'
  | 'interval:save';
