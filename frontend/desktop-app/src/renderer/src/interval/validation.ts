import { z } from 'zod';

import {
  POLL_MINUTES_MAX,
  POLL_MINUTES_MIN,
} from '../../../shared/config';

export const intervalSchema = z.object({
  minutes: z.coerce
    .number<string>({ error: 'Введите число минут' })
    .int('Только целое число минут')
    .min(
      POLL_MINUTES_MIN,
      `Не меньше ${POLL_MINUTES_MIN} мин`,
    )
    .max(
      POLL_MINUTES_MAX,
      `Не больше ${POLL_MINUTES_MAX} мин`,
    ),
});

export type IntervalInput = z.input<typeof intervalSchema>;
export type IntervalValues = z.output<
  typeof intervalSchema
>;
