import { z } from 'zod';

export const EVENT_PERIODS = [
  'none',
  'daily',
  'weekly',
  'monthly',
  'quarterly',
  'half_year',
  'yearly',
] as const;

export const createEventSchema = z.object({
  petId: z.string().min(1, 'Выберите питомца'),
  name: z
    .string()
    .trim()
    .min(1, 'Укажите название')
    .max(100, 'Не больше 100 символов'),
  schedule: z
    .string()
    .min(1, 'Укажите дату')
    .refine(
      (value) => !Number.isNaN(new Date(value).getTime()),
      'Укажите корректную дату',
    ),
  period: z.enum(EVENT_PERIODS),
});

export type CreateEventValues = z.infer<
  typeof createEventSchema
>;

const todayInputValue = () => {
  const date = new Date();
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 10);
};

export const createHealthEventSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, 'Укажите название')
      .max(255, 'Не больше 255 символов'),
    status: z.enum(['done', 'planned']),
    date: z.string().min(1, 'Укажите дату'),
    period: z.enum(EVENT_PERIODS),
    description: z
      .string()
      .max(2000, 'Не больше 2000 символов'),
  })
  .refine(
    // YYYY-MM-DD strings compare chronologically
    (values) =>
      values.status !== 'done' ||
      values.date <= todayInputValue(),
    {
      message:
        'Прошедшее событие не может быть в будущем — выберите «Запланировать»',
      path: ['date'],
    },
  );

export type CreateHealthEventValues = z.infer<
  typeof createHealthEventSchema
>;
