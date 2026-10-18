// Компактная версия frontend/app/login/page.tsx + AuthShell под окно 480px.
import markUrl from '../assets/petcare-mark.svg';
import { DemoLoginButtons } from './DemoLoginButtons';
import { LoginForm } from './LoginForm';

export function LoginPage() {
  return (
    <div className="min-h-screen bg-[var(--cream)] text-[var(--ink)]">
      <header className="border-b border-[var(--ink)] bg-[var(--forest)] text-[var(--cream)]">
        <div className="flex min-h-16 items-center gap-3 px-5 py-3">
          <span className="grid size-10 place-items-center bg-[var(--forest)]">
            <img
              src={markUrl}
              alt=""
              width={40}
              height={40}
              className="size-full object-contain"
            />
          </span>
          <span className="font-mono text-xs font-bold uppercase tracking-[0.22em]">
            petcare
          </span>
        </div>
      </header>
      <section className="border-b border-[var(--ink)] bg-[var(--forest)] px-5 py-8 text-[var(--cream)]">
        <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--lime)]">
          С возвращением
        </p>
        <h1 className="mt-5 text-5xl font-black leading-[0.85] tracking-[-0.055em]">
          Всё важное — рядом.
        </h1>
        <p className="mt-5 text-base leading-[1.4] text-[var(--cream)]/75">
          Войдите, чтобы продолжить заботу о питомце без
          лишних поисков и напоминаний.
        </p>
      </section>
      <main className="bg-[var(--white)] px-5 py-8">
        <div className="space-y-8">
          <LoginForm />
          <DemoLoginButtons />
        </div>
      </main>
    </div>
  );
}
