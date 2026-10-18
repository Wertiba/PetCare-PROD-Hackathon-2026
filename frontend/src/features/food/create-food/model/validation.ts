import { z } from 'zod';

const assessment = z.enum(['yes', 'no', 'unknown']);

export const createFoodSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Укажите корм')
    .max(255, 'Не больше 255 символов'),
  weight: z
    .string()
    .trim()
    .refine(
      (value) => value === '' || /^\d+$/.test(value),
      'Порция — целое число граммов',
    )
    // The backend stores the portion as a 32-bit integer.
    .refine(
      (value) =>
        value === '' || Number(value) <= 2_147_483_647,
      'Слишком большая порция',
    ),
  isApproach: assessment.nullable(),
  isTolerability: assessment.nullable(),
  reactions: z.array(z.string()),
  details: z.string().max(500, 'Не больше 500 символов'),
  ingredients: z
    .string()
    .refine(
      (value) => value.split(',').length <= 100,
      'Не больше 100 ингредиентов',
    )
    .refine(
      (value) =>
        value
          .split(',')
          .every((item) => item.trim().length <= 100),
      'Каждый ингредиент — не больше 100 символов',
    ),
});

export type CreateFoodValues = z.infer<
  typeof createFoodSchema
>;
