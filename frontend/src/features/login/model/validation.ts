import { z } from 'zod';

export const loginSchema = z.object({
  login: z.string(),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters long'),
});

export type LoginValues = z.infer<typeof loginSchema>;
