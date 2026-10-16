import { z } from 'zod';

const EMAIL_MAX_LENGTH = 254;
const PASSWORD_MIN_LENGTH = 8;
const PASSWORD_MAX_LENGTH = 72;

/** Same pattern as the backend's `fullName` field validation. */
const FULL_NAME_PATTERN = /^[а-яА-Яa-zA-Z0-9 _-]{2,200}$/;

export const registerSchema = z.object({
  email: z
    .email('Enter a valid email address')
    .max(
      EMAIL_MAX_LENGTH,
      `Email must be at most ${EMAIL_MAX_LENGTH} characters`,
    ),
  password: z
    .string()
    .min(
      PASSWORD_MIN_LENGTH,
      `Password must be between ${PASSWORD_MIN_LENGTH} and ${PASSWORD_MAX_LENGTH} characters`,
    )
    .max(
      PASSWORD_MAX_LENGTH,
      `Password must be between ${PASSWORD_MIN_LENGTH} and ${PASSWORD_MAX_LENGTH} characters`,
    )
    .regex(
      /[A-Za-z]/,
      'Password must contain at least one letter',
    )
    .regex(
      /\d/,
      'Password must contain at least one digit',
    ),
  fullName: z
    .string()
    .trim()
    .min(1, 'Full name is required')
    .regex(
      FULL_NAME_PATTERN,
      'Full name must be 2-200 characters and contain only letters, digits, spaces, underscores or hyphens',
    ),
});

export type RegisterValues = z.infer<typeof registerSchema>;
