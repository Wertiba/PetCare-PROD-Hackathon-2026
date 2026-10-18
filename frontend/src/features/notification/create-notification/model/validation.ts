import { z } from 'zod';

export const NOTIFICATION_TYPES = [
  'app',
  'telegram',
  'web_push',
] as const;

export const createNotificationSchema = z.object({
  type: z.enum(NOTIFICATION_TYPES),
  time: z
    .string()
    .min(1, 'Укажите дату и время')
    .refine(
      (value) => !Number.isNaN(new Date(value).getTime()),
      'Некорректная дата',
    ),
});

export type CreateNotificationValues = z.infer<
  typeof createNotificationSchema
>;
