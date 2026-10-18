import { fetchPetReport } from '@src/entities/pet/api';
import { useMutation } from '@tanstack/react-query';

export const useDownloadReportMutation = () =>
  useMutation({
    mutationFn: fetchPetReport,
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'petcare-report.pdf';
      link.click();
      URL.revokeObjectURL(url);
    },
  });
