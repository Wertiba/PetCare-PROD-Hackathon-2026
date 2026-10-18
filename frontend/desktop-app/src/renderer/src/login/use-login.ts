import { useState } from 'react';

import type { LoginValues } from './validation';

/** Login through the main process; on success it closes this window. */
export function useLogin() {
  const [isPending, setPending] = useState(false);
  const [error, setError] = useState(false);

  const mutate = (values: LoginValues) => {
    setPending(true);
    setError(false);
    window.loginApi
      .login(values)
      .then(
        (ok) => setError(!ok),
        () => setError(true),
      )
      .finally(() => setPending(false));
  };

  return { mutate, isPending, error };
}
