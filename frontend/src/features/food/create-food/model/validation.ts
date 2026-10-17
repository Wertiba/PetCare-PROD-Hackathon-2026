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
    ),
  isApproach: assessment,
  isTolerability: assessment,
  reactions: z.array(z.string()),
  details: z.string().max(500, 'Не больше 500 символов'),
  ingredients: z.string(),
});

export type CreateFoodValues = z.infer<
  typeof createFoodSchema
>;
