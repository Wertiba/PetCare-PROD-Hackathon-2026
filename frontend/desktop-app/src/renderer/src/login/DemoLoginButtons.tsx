// Копия frontend/src/features/login/ui/DemoLoginButtons.tsx:
// сетка в 5 колонок под узкое окно.
import { demoUsers } from './demo-users';
import { useLogin } from './use-login';

export function DemoLoginButtons() {
  const { mutate, isPending, error } = useLogin();

  return (
    <section
      aria-labelledby="demo-access-title"
      className="border-t border-[var(--ink)] pt-7"
    >
      <p
        id="demo-access-title"
        className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-[var(--forest)]/70"
      >
        Быстрый вход для проверки
      </p>
      <div className="mt-4 grid grid-cols-5 gap-2">
        {demoUsers.map((user) => (
          <button
            key={user.login}
            type="button"
            disabled={isPending}
            onClick={() => mutate(user)}
            className="border border-[var(--ink)] bg-[var(--cream)] px-1 py-3 text-sm font-bold tracking-[0.01em] text-[var(--forest)] transition-transform hover:-translate-y-0.5 hover:bg-[var(--lime)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--forest)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {user.login}
          </button>
        ))}
      </div>
      {error ? (
        <p
          role="alert"
          className="mt-4 text-sm leading-5 text-red-700"
        >
          Не удалось выполнить быстрый вход. Попробуйте ещё
          раз.
        </p>
      ) : null}
    </section>
  );
}
