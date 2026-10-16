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
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={fieldId}
        className="text-sm text-neutral-600"
      >
        {label}
      </label>
      <input
        ref={ref}
        id={fieldId}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        className="w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm text-black placeholder:text-neutral-400 focus:border-neutral-500 focus:outline-none"
        {...inputProps}
      />
      {error ? (
        <span
          id={errorId}
          role="alert"
          className="text-xs text-red-600"
        >
          {error}
        </span>
      ) : null}
    </div>
  );
});
