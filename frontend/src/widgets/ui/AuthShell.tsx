import Image from 'next/image';
import Link from 'next/link';

interface AuthShellProps {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
}

/** Общая разметка страниц входа: шапка и центральная форма. */
export function AuthShell({
  eyebrow,
  title,
  description,
  children,
}: AuthShellProps) {
  return (
    <div className="min-h-screen bg-[var(--cream)] text-[var(--ink)]">
      <header className="border-b border-[var(--ink)] bg-[var(--forest)] text-[var(--cream)]">
        <div className="mx-auto flex min-h-16 w-full max-w-[1440px] items-center justify-between px-5 py-3 sm:px-8 lg:px-12">
          <Link
            href="/"
            className="group flex items-center gap-3"
          >
            <span className="grid size-10 place-items-center bg-[var(--forest)] transition-transform group-hover:-rotate-6">
              <Image
                src="/images/petcare-mark.svg"
                alt=""
                width={40}
                height={40}
                className="size-full object-contain"
              />
            </span>
            <span className="font-mono text-xs font-bold uppercase tracking-[0.22em]">
              petcare
            </span>
          </Link>
          <Link
            href="/"
            className="text-sm font-semibold tracking-[0.01em] text-[var(--cream)]/80 underline decoration-[var(--lime)] decoration-2 underline-offset-4 transition-colors hover:text-[var(--lime)]"
          >
            На главную
          </Link>
        </div>
      </header>
      <main className="mx-auto grid w-full max-w-[1440px] xl:min-h-[calc(100vh-4rem)] xl:grid-cols-[minmax(0,5fr)_minmax(0,4fr)]">
        <section className="flex min-h-[360px] flex-col justify-between border-b border-[var(--ink)] bg-[var(--forest)] px-5 py-10 text-[var(--cream)] sm:px-8 sm:py-14 xl:min-h-0 xl:border-b-0 xl:border-r xl:px-12 xl:py-16">
          <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--lime)]">
            {eyebrow}
          </p>
          <div className="mt-14 max-w-[620px] xl:mt-0">
            <h1 className="text-[clamp(3.8rem,7vw,7.8rem)] font-black leading-[0.8] tracking-[-0.055em]">
              {title}
            </h1>
            <p className="mt-8 max-w-[370px] text-[clamp(1.1rem,1.5vw,1.28rem)] leading-[1.4] text-[var(--cream)]/75">
              {description}
            </p>
          </div>
          <p className="mt-14 max-w-[330px] border-t border-[var(--cream)]/35 pt-5 text-sm leading-6 text-[var(--cream)]/65 xl:mt-0">
            Все важные детали о питомце — в одном спокойном
            месте.
          </p>
        </section>
        <section className="flex items-center bg-[var(--white)] px-5 py-12 sm:px-8 sm:py-16 xl:px-12">
          <div className="mx-auto w-full max-w-[470px]">
            {children}
          </div>
        </section>
      </main>
    </div>
  );
}
