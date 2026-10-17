'use client';

import { forwardRef } from 'react';

interface FormFieldProps extends React.ComponentPropsWithoutRef<'input'> {
  label: string;
  error?: string;
}

export const FormField = forwardRef<
  HTMLInputElement,
  FormFieldProps
>(function FormField(
  { label, error, id, ...inputProps },
  ref,
) {
  const fieldId = id ?? inputProps.name;
  const errorId = fieldId ? `${fieldId}-error` : undefined;

  return (
    <div className="flex flex-col gap-2">
      <label
        htmlFor={fieldId}
        className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
      >
        {label}
      </label>
      <input
        ref={ref}
        id={fieldId}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        className="w-full border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
        {...inputProps}
      />
      {error ? (
        <span
          id={errorId}
          role="alert"
          className="text-sm text-red-700"
        >
          {error}
        </span>
      ) : null}
    </div>
  );
});
