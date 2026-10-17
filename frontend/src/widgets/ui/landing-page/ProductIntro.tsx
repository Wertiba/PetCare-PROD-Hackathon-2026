import { careSteps } from '@src/shared/config';
import Image from 'next/image';

export default function ProductIntro() {
  return (
    <section
      id="why"
      className="overflow-hidden border-b border-[var(--ink)] bg-[var(--white)]"
    >
      <div className="mx-auto grid w-full max-w-[1440px] md:grid-cols-2 xl:grid-cols-[minmax(0,5.1fr)_minmax(0,4.3fr)_minmax(0,2.6fr)]">
        <div className="relative flex min-h-[440px] flex-col justify-between border-b border-[var(--ink)] px-5 py-12 sm:px-8 md:col-span-2 md:min-h-[470px] xl:col-span-1 xl:min-h-[660px] xl:border-b-0 xl:border-r xl:px-12 xl:py-16">
          <div className="flex items-center gap-3 font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--forest)]/65">
            <span className="size-3 border border-[var(--ink)] bg-[var(--lime)]" />
            Зачем это нужно
          </div>
          <h2 className="relative z-10 max-w-full text-[clamp(4.2rem,6vw,7.32rem)] font-black leading-[0.82] tracking-[-0.07em] text-[var(--forest)]">
            <span className="block">Забота</span>
            <span className="block">становится</span>
            <span className="block w-fit bg-[var(--lime)] px-2 text-[var(--ink)] shadow-[5px_5px_0_var(--ink)]">
              проще.
            </span>
          </h2>
          <p className="max-w-[360px] border-t border-[var(--ink)] pt-6 text-[clamp(1.1rem,1.4vw,1.25rem)] leading-[1.38] text-[var(--ink)]/75">
            Когда история питомца, питание и будущие
            процедуры собраны в одном месте.
          </p>
          <span className="absolute bottom-12 right-[-20px] hidden size-10 rotate-45 border border-[var(--ink)] bg-[var(--lime)] xl:block" />
        </div>
        <div className="relative min-h-[500px] border-b border-[var(--ink)] bg-[var(--cream)] md:border-r xl:min-h-[660px] xl:border-b-0">
          <Image
            src="/images/petcare-notes.png"
            alt="Блокнот, поводок и жетон для заметок о питомце"
            fill
            className="object-cover"
            sizes="(max-width: 767px) 100vw, (max-width: 1279px) 50vw, 36vw"
          />
          <div className="absolute bottom-5 left-5 max-w-[210px] border border-[var(--ink)] bg-[var(--cream)] p-4 font-mono text-[10px] font-bold uppercase leading-[1.5] tracking-[0.13em] text-[var(--forest)] shadow-[5px_5px_0_var(--ink)] sm:bottom-8 sm:left-8">
            Всё нужное — не в голове, а под рукой.
          </div>
        </div>
        <div className="flex min-h-[360px] flex-col bg-[var(--lime)] md:min-h-[500px] xl:min-h-[660px]">
          <ol className="grid grid-cols-3 border-b border-[var(--ink)] xl:grid-cols-1">
            {careSteps.map(({ number, label }, index) => (
              <li
                key={number}
                className={`p-4 sm:p-6 xl:flex xl:items-baseline xl:gap-5 xl:px-8 xl:py-5 ${index < careSteps.length - 1 ? 'border-r border-[var(--ink)] xl:border-b xl:border-r-0' : ''}`}
              >
                <span className="block font-mono text-xl font-black leading-none tracking-[-0.08em] text-[var(--forest)]">
                  {number}
                </span>
                <span className="mt-2 block text-sm font-bold leading-[1.15] text-[var(--forest)] xl:mt-0">
                  {label}
                </span>
              </li>
            ))}
          </ol>
          <div className="flex flex-1 flex-col justify-end p-5 sm:p-8 xl:p-8">
            <p className="max-w-[320px] text-[clamp(1.2rem,1.65vw,1.5rem)] leading-[1.32] text-[var(--forest)]">
              Меньше поисков по чатам и заметкам. Больше
              спокойствия в повседневной заботе.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
