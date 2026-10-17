import type {
  EventPeriod,
  EventStatus,
  EventType,
} from './event.types';

export const eventTypeLabels: Record<EventType, string> = {
  vaccination: 'Прививка',
  parasite_treatment: 'Обработка от паразитов',
  vet_visit: 'Визит к врачу',
  medication: 'Препарат',
  grooming: 'Груминг',
  other: 'Другое',
};

export const eventStatusLabels: Record<
  EventStatus,
  string
> = {
  planned: 'Запланировано',
  done: 'Выполнено',
  skipped: 'Пропущено',
  cancelled: 'Отменено',
};

export const eventPeriodLabels: Record<
  EventPeriod,
  string
> = {
  none: 'Не повторять',
  daily: 'Каждый день',
  weekly: 'Каждую неделю',
  monthly: 'Каждый месяц',
  quarterly: 'Раз в 3 месяца',
  half_year: 'Раз в полгода',
  yearly: 'Раз в год',
};
