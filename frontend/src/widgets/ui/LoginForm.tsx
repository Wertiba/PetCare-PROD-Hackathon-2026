'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useLoginMutation } from '@src/features/login';
import type { LoginValues } from '@src/features/login';
import { loginSchema } from '@src/features/login/model/validation';
import { FormField, SubmitButton } from '@src/shared/ui';
import Link from 'next/link';
import { useForm } from 'react-hook-form';

import { whiteLinkClasses } from './Header';

const INITIAL_VALUES: LoginValues = {
  email: '',
  password: '',
};

export function LoginForm() {
  const { mutate, isPending, error } = useLoginMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    defaultValues: INITIAL_VALUES,
    mode: 'onTouched',
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (values: LoginValues) => {
    // setFormError(null);

    mutate(values);
  };

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
      className="flex flex-col gap-6"
      noValidate
    >
      <FormField
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="you@example.com"
        error={errors.email?.message}
        {...register('email')}
      />
      <FormField
        label="Password"
        type="password"
        autoComplete="current-password"
        placeholder="Your password"
        error={errors.password?.message}
        {...register('password')}
      />

      {error ? (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="signing in…"
      >
        sign in
      </SubmitButton>

      <p className="mt-1 text-center text-sm text-neutral-600">
        no account?{' '}
        <Link href="/register" className={whiteLinkClasses}>
          create one
        </Link>
      </p>
    </form>
  );
}
