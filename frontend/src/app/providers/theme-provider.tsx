'use client';

import { getStoredTheme } from '@src/shared/lib/theme';
import { useEffect } from 'react';

export function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    document.documentElement.dataset.theme =
      getStoredTheme();
  }, []);

  return <>{children}</>;
}
