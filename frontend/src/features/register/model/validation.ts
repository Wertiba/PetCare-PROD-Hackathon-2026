import { z } from 'zod';

const PASSWORD_MIN_LENGTH = 8;
const PASSWORD_MAX_LENGTH = 72;

/** Same pattern as the backend's `fullName` field validation. */
const FULL_NAME_PATTERN = /^[а-яА-ЯёЁa-zA-Z0-9 _-]{2,200}$/;

export const registerSchema = z.object({
  login: z
    .string()
    .min(6, 'Логин должен содержать не менее 6 символов'),
  password: z
    .string()
    .min(
      PASSWORD_MIN_LENGTH,
      `Пароль должен содержать от ${PASSWORD_MIN_LENGTH} до ${PASSWORD_MAX_LENGTH} символов`,
    )
    .max(
      PASSWORD_MAX_LENGTH,
      `Пароль должен содержать от ${PASSWORD_MIN_LENGTH} до ${PASSWORD_MAX_LENGTH} символов`,
    )
    .regex(
      /[A-Za-z]/,
      'Пароль должен содержать хотя бы одну латинскую букву',
    )
    .regex(
      /\d/,
      'Пароль должен содержать хотя бы одну цифру',
    ),
  fullName: z
    .string()
    .trim()
    .min(1, 'Укажите имя')
    .regex(
      FULL_NAME_PATTERN,
      'Имя должно содержать от 2 до 200 символов: буквы, цифры, пробелы, «_» или «-».',
    ),
});

export type RegisterValues = z.infer<typeof registerSchema>;
