import { z } from 'zod';

export const createPetSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Name is required')
    .max(100, 'Name must be at most 100 characters long'),
  animalId: z.string().min(1, 'Animal is required'),
  breedId: z.string().min(1, 'Breed is required'),
  birthDate: z
    .string()
    .min(1, 'Birth date is required')
    .refine(
      (value) => new Date(value).getTime() <= Date.now(),
      'Birth date must not be in the future',
    ),
});

export type CreatePetValues = z.infer<
  typeof createPetSchema
>;
