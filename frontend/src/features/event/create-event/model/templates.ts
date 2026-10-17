import type { EventType } from '@src/entities/event';

// Quick-pick names only: intervals and doses always come from the owner or the vet.
export const eventNameTemplates: Record<
  EventType,
  string[]
> = {
  vaccination: [
    'Комплексная вакцина',
    'Бешенство',
    'Ревакцинация',
  ],
  parasite_treatment: [
    'От блох и клещей',
    'От глистов',
    'Комплексная обработка',
  ],
  vet_visit: [
    'Плановый осмотр',
    'Консультация',
    'Анализы',
    'Повторный приём',
  ],
  medication: ['Курс препарата', 'Витамины', 'Капли'],
  grooming: [
    'Стрижка',
    'Стрижка когтей',
    'Купание',
    'Чистка ушей',
  ],
  other: [],
};
