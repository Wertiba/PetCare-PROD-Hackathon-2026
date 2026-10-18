import { z } from 'zod';

export const loginSchema = z.object({
  login: z.string(),
  password: z
    .string()
    .min(8, 'Пароль должен содержать не менее 8 символов'),
});

export type LoginValues = z.infer<typeof loginSchema>;
