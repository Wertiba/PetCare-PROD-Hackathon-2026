import { z } from 'zod';

export const toNumber = (value: string) =>
  Number(value.trim().replace(',', '.'));

export const todayInputValue = () => {
  const date = new Date();
  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60_000,
  )
    .toISOString()
    .slice(0, 10);
};

export const addWeightSchema = z.object({
  value: z
    .string()
    .trim()
    .min(1, 'Укажите вес')
    .refine(
      (value) => toNumber(value) > 0,
      'Вес должен быть положительным числом',
    ),
  unit: z.enum(['kg', 'g']),
  date: z
    .string()
    .min(1, 'Укажите дату')
    .refine(
      // YYYY-MM-DD strings compare chronologically
      (value) => value <= todayInputValue(),
      'Дата не может быть в будущем',
    ),
});

export type AddWeightValues = z.infer<
  typeof addWeightSchema
>;
