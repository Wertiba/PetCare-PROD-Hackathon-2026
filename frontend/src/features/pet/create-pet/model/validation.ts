import { z } from 'zod';

export const createPetSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Укажите кличку')
    .max(100, 'Не больше 100 символов'),
  animalId: z.string().min(1, 'Выберите вид животного'),
  breedId: z.string().min(1, 'Выберите породу'),
  birthDate: z
    .string()
    .min(1, 'Укажите дату рождения')
    .refine(
      (value) => new Date(value).getTime() <= Date.now(),
      'Дата рождения не может быть в будущем',
    ),
});

export type CreatePetValues = z.infer<
  typeof createPetSchema
>;
