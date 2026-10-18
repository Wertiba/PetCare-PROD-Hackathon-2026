import { z } from 'zod';

const FULL_NAME_PATTERN = /^[а-яА-ЯёЁa-zA-Z0-9 _-]{2,200}$/;

export const updateFullNameSchema = z.object({
  fullName: z
    .string()
    .trim()
    .regex(
      FULL_NAME_PATTERN,
      'Имя должно содержать от 2 до 200 символов: буквы, цифры, пробелы, «_» или «-».',
    ),
});

export type UpdateFullNameValues = z.infer<
  typeof updateFullNameSchema
>;
