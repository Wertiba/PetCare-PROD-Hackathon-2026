'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { FormField, SubmitButton } from '@src/shared/ui';
import Link from 'next/link';
import { useForm } from 'react-hook-form';

import { useRegisterMutation } from '../model/use-register-mutation';
import {
  type RegisterValues,
  registerSchema,
} from '../model/validation';

const INITIAL_VALUES: RegisterValues = {
  fullName: '',
  login: '',
  password: '',
};

const AUTH_LINK_CLASSES =
  'font-bold text-[var(--forest)] underline decoration-[var(--lime)] decoration-2 underline-offset-4 transition-colors hover:text-[var(--ink)]';

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
      fullName: values.fullName.trim(),
      login: values.login.trim(),
    });
  };

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
      className="flex flex-col gap-5"
      noValidate
    >
      <FormField
        label="Имя"
        type="text"
        autoComplete="name"
        placeholder="Введите имя"
        error={errors.fullName?.message}
        {...register('fullName')}
      />
      <FormField
        label="Логин"
        type="text"
        autoComplete="username"
        placeholder="Введите логин"
        error={errors.login?.message}
        {...register('login')}
      />
      <FormField
        label="Пароль"
        type="password"
        autoComplete="new-password"
        placeholder="Введите пароль"
        error={errors.password?.message}
        {...register('password')}
      />

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось создать аккаунт. Проверьте данные и
          попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Создаём аккаунт…"
      >
        Создать аккаунт
      </SubmitButton>

      <p className="mt-2 text-sm text-[var(--ink)]/70">
        Уже есть аккаунт?{' '}
        <Link href="/login" className={AUTH_LINK_CLASSES}>
          Войти
        </Link>
      </p>
    </form>
  );
}
