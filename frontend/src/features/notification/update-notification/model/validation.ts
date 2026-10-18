import { z } from 'zod';

export const UPDATE_NOTIFICATION_TYPES = [
  'app',
  'telegram',
  'web_push',
] as const;

export const updateNotificationSchema = z.object({
  type: z.enum(UPDATE_NOTIFICATION_TYPES),
  time: z
    .string()
    .min(1, 'Укажите дату и время')
    .refine(
      (value) => !Number.isNaN(new Date(value).getTime()),
      'Некорректная дата',
    ),
});

export type UpdateNotificationValues = z.infer<
  typeof updateNotificationSchema
>;
