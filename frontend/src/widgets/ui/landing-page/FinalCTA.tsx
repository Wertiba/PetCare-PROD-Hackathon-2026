import { careSteps } from '@src/shared/config';
import { ActionLink } from '@src/shared/ui';

export default function FinalCTA() {
  return (
    <section className="overflow-hidden border-t border-[var(--ink)] bg-[var(--cream)] text-[var(--ink)]">
      <div className="mx-auto grid w-full max-w-[1440px] xl:grid-cols-12">
        <div className="flex min-h-[560px] flex-col border-b border-[var(--ink)] px-5 py-12 sm:px-8 xl:col-span-8 xl:min-h-[640px] xl:border-b-0 xl:border-r xl:px-12 xl:py-16">
          <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--forest)]/65">
            Начните с малого
          </p>
          <div className="mt-auto">
            <h2 className="max-w-[850px] text-[clamp(4.2rem,7.8vw,9.5rem)] font-black leading-[0.76] tracking-[-0.075em] text-[var(--forest)]">
              Держите важное
              <span className="block text-[var(--ink)]">
                рядом.
              </span>
            </h2>
            <div className="mt-[clamp(5rem,8vw,7rem)] flex flex-col items-start gap-7 sm:flex-row sm:items-end sm:justify-between">
              <p className="max-w-[350px] text-[clamp(1.1rem,1.4vw,1.25rem)] leading-[1.38] text-[var(--ink)]/75">
                Создайте аккаунт и соберите заботу о питомце
                в одном спокойном месте.
              </p>
              <ActionLink href="/register">
                Создать аккаунт
              </ActionLink>
            </div>
          </div>
        </div>
        <div className="flex min-h-[330px] flex-col bg-[var(--lime)] xl:col-span-4 xl:min-h-[640px] xl:p-12">
          <ol className="grid grid-cols-3 border-b border-[var(--forest)] xl:grid-cols-1">
            {careSteps.map(
              ({ number, compactLabel }, index) => (
                <li
                  key={number}
                  className={`p-5 sm:p-8 xl:flex xl:items-baseline xl:gap-6 xl:px-0 xl:py-5 ${index < careSteps.length - 1 ? 'border-r border-[var(--forest)] xl:border-b xl:border-r-0' : ''}`}
                >
                  <span className="font-mono text-2xl font-black leading-none tracking-[-0.1em] text-[var(--forest)]">
                    {number}
                  </span>
                  <span className="mt-2 block text-xs font-bold leading-[1.15] text-[var(--forest)] xl:mt-0 xl:text-sm">
                    {compactLabel}
                  </span>
                </li>
              ),
            )}
          </ol>
          <div className="flex flex-1 flex-col justify-end p-5 sm:p-8 xl:px-0 xl:pb-0">
            <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--forest)]/70">
              petcare / для каждого дня
            </p>
            <p className="mt-4 max-w-[330px] text-[clamp(1.65rem,2.3vw,2.35rem)] font-black leading-[0.96] tracking-[-0.03em] text-[var(--forest)]">
              Всё для заботы рядом.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
