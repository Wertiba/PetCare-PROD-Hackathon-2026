'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useRegisterMutation } from '@src/features/register';
import type { RegisterValues } from '@src/features/register';
import { registerSchema } from '@src/features/register/model/validation';
import { FormField, SubmitButton } from '@src/shared/ui';
import Link from 'next/link';
import { useForm } from 'react-hook-form';

import { whiteLinkClasses } from './Header';

const INITIAL_VALUES: RegisterValues = {
  login: '',
  password: '',
  fullName: '',
};

export function RegisterForm() {
  const { mutate, isPending, error } =
    useRegisterMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterValues>({
    defaultValues: INITIAL_VALUES,
    mode: 'onTouched',
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (values: RegisterValues) => {
    mutate({
      ...values,
      login: values.login.trim(),
      fullName: values.fullName.trim(),
    });
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
        label="Full name"
        type="text"
        autoComplete="name"
        placeholder="Ivan Ivanov"
        error={errors.fullName?.message}
        {...register('fullName')}
      />
      <FormField
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="you@example.com"
        error={errors.login?.message}
        {...register('login')}
      />
      <FormField
        label="Password"
        type="password"
        autoComplete="new-password"
        placeholder="At least 8 characters"
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
        pendingLabel="creating account…"
      >
        create account
      </SubmitButton>

      <p className="mt-1 text-center text-sm text-neutral-600">
        already have an account?{' '}
        <Link href="/login" className={whiteLinkClasses}>
          log in
        </Link>
      </p>
    </form>
  );
}
