// Копия frontend/src/features/login/ui/LoginForm.tsx:
// мутация — через main-процесс, ссылка на регистрацию — в браузер.
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';

import { APP_URL } from '../../../shared/config';
import { FormField, SubmitButton } from '../ui';
import { useLogin } from './use-login';
import {
  type LoginValues,
  loginSchema,
} from './validation';

const INITIAL_VALUES: LoginValues = {
  login: '',
  password: '',
};

const AUTH_LINK_CLASSES =
  'font-bold text-[var(--forest)] underline decoration-[var(--lime)] decoration-2 underline-offset-4 transition-colors hover:text-[var(--ink)]';

export function LoginForm() {
  const { mutate, isPending, error } = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    defaultValues: INITIAL_VALUES,
    mode: 'onTouched',
    resolver: zodResolver(loginSchema),
  });

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit((values) => mutate(values))(
          event,
        );
      }}
      className="flex flex-col gap-5"
      noValidate
    >
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
        autoComplete="current-password"
        placeholder="Введите пароль"
        error={errors.password?.message}
        {...register('password')}
      />

      {error ? (
        <p
          role="alert"
          className="border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800"
        >
          Не удалось войти. Проверьте логин и пароль и
          попробуйте ещё раз.
        </p>
      ) : null}

      <SubmitButton
        pending={isPending}
        pendingLabel="Выполняем вход…"
      >
        Войти
      </SubmitButton>

      <p className="mt-2 text-sm text-[var(--ink)]/70">
        Нет аккаунта?{' '}
        <a
          href={`${APP_URL}/register`}
          target="_blank"
          rel="noreferrer"
          className={AUTH_LINK_CLASSES}
        >
          Создать
        </a>
      </p>
    </form>
  );
}
