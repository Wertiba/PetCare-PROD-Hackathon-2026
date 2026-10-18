import type { FetchEventsCalendarReqDto } from '@src/entities/event/api';
import { fetchEventsCalendar } from '@src/entities/event/api';
import { useMutation } from '@tanstack/react-query';

export const useDownloadCalendarMutation = () =>
  useMutation({
    mutationFn: (query: FetchEventsCalendarReqDto) =>
      fetchEventsCalendar(query),
    onSuccess: (blob, { petId }) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = petId
        ? `petcare-${petId}.ics`
        : 'petcare.ics';
      link.click();
      URL.revokeObjectURL(url);
    },
  });
