'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import { ActionLink } from '@src/shared/ui';
import Image from 'next/image';

export default function HeroSection() {
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );
  const actionHref = user ? '/dashboard' : '/register';
  const actionLabel = user
    ? 'Перейти к питомцам'
    : 'Создать аккаунт';

  return (
    <section className="relative overflow-hidden bg-[var(--cream)]">
      <div className="mx-auto grid min-h-[680px] w-full max-w-[1440px] grid-cols-1 xl:grid-cols-2">
        <div className="relative z-10 flex flex-col justify-between px-5 pb-12 pt-16 sm:px-8 sm:pt-20 xl:px-12 xl:pb-16 xl:pt-20">
          <div>
            <p className="mb-9 max-w-[205px] font-mono text-xs font-bold uppercase leading-[1.5] tracking-[0.16em] text-[var(--forest)]/65">
              Небольшое место для заботы каждый день
            </p>
            <h1 className="max-w-full text-[clamp(4.08rem,6.24vw,7.8rem)] font-black leading-[0.84] tracking-[-0.065em] text-[var(--forest)]">
              <span className="block">Забота</span>
              <span className="block">начинается</span>
              <span className="block text-[var(--ink)]">
                с мелочей.
              </span>
            </h1>
          </div>
          <div className="mt-14 flex max-w-[620px] flex-col gap-7 sm:mt-16 sm:flex-row sm:items-end sm:gap-10 xl:mt-20">
            <p className="max-w-[330px] text-[clamp(1.1rem,1.4vw,1.25rem)] leading-[1.38] text-[var(--ink)]/75">
              Удобное место для заметок о питомце,
              ежедневных привычек и всего, что важно не
              забыть.
            </p>
            {isSessionRestored ? (
              <ActionLink
                href={actionHref}
                emphasis="hero"
                className="sm:ml-auto"
              >
                {actionLabel}
              </ActionLink>
            ) : (
              <span
                aria-hidden="true"
                className="h-14 w-56 animate-pulse bg-[var(--forest)]/10 sm:ml-auto"
              />
            )}
          </div>
        </div>
        <div className="relative min-h-[480px] overflow-hidden border-t border-[var(--ink)] bg-[var(--forest)] sm:min-h-[560px] xl:min-h-0 xl:border-l xl:border-t-0">
          <Image
            src="/images/petcare-hero.png"
            alt="Счастливая собака выглядывает из-за рваного кремового листа"
            fill
            priority
            className="object-cover object-center"
            sizes="(max-width: 1279px) 100vw, 58vw"
          />
          <div className="absolute left-5 top-5 border border-[var(--ink)] bg-[var(--lime)] px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--forest)] shadow-[4px_4px_0_var(--ink)] sm:left-8 sm:top-8">
            для каждого дня
          </div>
          <div className="absolute bottom-5 right-5 grid size-24 rotate-[-9deg] place-items-center border border-[var(--ink)] bg-[var(--cream)] text-center font-mono text-[10px] font-bold uppercase leading-[1.2] tracking-[0.08em] text-[var(--forest)] shadow-[5px_5px_0_var(--ink)] sm:bottom-8 sm:right-8">
            важные
            <br />
            мелочи
          </div>
        </div>
      </div>
      <div className="border-y border-[var(--ink)] bg-[var(--lime)]">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-5 px-5 py-3 font-mono text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--forest)] sm:px-8 lg:px-12">
          <span>хорошее место для начала</span>
          <span className="hidden sm:inline">
            листайте дальше ↓
          </span>
        </div>
      </div>
    </section>
  );
}
