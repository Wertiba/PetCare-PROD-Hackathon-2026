const features = [
  {
    number: '01',
    title: 'Питомец — в центре',
    text: 'Профиль, история здоровья и питание связаны с конкретным питомцем — без путаницы.',
    tone: 'bg-[var(--forest)] text-[var(--cream)]',
    accent: 'bg-[var(--lime)] text-[var(--forest)]',
  },
  {
    number: '02',
    title: 'История здоровья',
    text: 'Вакцинации, обработки, приёмы у ветеринара и важные записи остаются в хронологии.',
    tone: 'bg-[var(--lime)] text-[var(--forest)]',
    accent: 'bg-[var(--forest)] text-[var(--cream)]',
  },
  {
    number: '03',
    title: 'Напоминания вовремя',
    text: 'Будущие процедуры и назначенные лекарства видны заранее, когда это действительно важно.',
    tone: 'bg-[var(--white)] text-[var(--ink)]',
    accent: 'bg-[var(--ink)] text-[var(--cream)]',
  },
];

export default function FeatureShowcase() {
  return (
    <section
      id="inside"
      className="overflow-hidden bg-[var(--forest)] text-[var(--cream)]"
    >
      <div className="mx-auto grid w-full max-w-[1440px] xl:grid-cols-12">
        <div className="flex min-h-[470px] flex-col justify-between border-b border-[var(--cream)]/35 px-5 py-12 sm:px-8 xl:col-span-5 xl:min-h-[670px] xl:border-b-0 xl:border-r xl:px-12 xl:py-16">
          <div>
            <p className="font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-[var(--lime)]">
              Что уже есть в PetCare
            </p>
            <h2 className="mt-8 max-w-[720px] text-[clamp(3.4rem,7.4vw,6.25rem)] font-black leading-[0.78] tracking-[-0.07em]">
              Всё важное —
              <span className="block text-[var(--lime)]">
                вместе.
              </span>
            </h2>
          </div>
          <p className="max-w-[370px] border-t border-[var(--cream)]/35 pt-6 text-[clamp(1.1rem,1.4vw,1.25rem)] leading-[1.38] text-[var(--cream)]/75">
            Не три отдельных списка, а единая картина жизни
            вашего питомца.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 xl:col-span-7 xl:grid-rows-2">
          <article
            className={`min-h-[350px] border-b border-[var(--ink)] p-6 shadow-[7px_7px_0_var(--ink)] sm:col-span-2 sm:p-8 xl:min-h-0 ${features[0].tone}`}
          >
            <div className="flex items-start justify-between gap-4">
              <span
                className={`grid size-12 place-items-center border border-[var(--ink)] font-mono text-xs font-bold ${features[0].accent}`}
              >
                {features[0].number}
              </span>
              <span className="font-mono text-[11px] uppercase tracking-[0.16em] opacity-60">
                профиль питомца
              </span>
            </div>
            <div className="mt-16 max-w-[540px] sm:mt-20">
              <h3 className="text-[clamp(3rem,4.5vw,4.5rem)] font-black leading-[0.9] tracking-[-0.04em]">
                {features[0].title}
              </h3>
              <p className="mt-7 max-w-[450px] text-[1.05rem] leading-[1.45] opacity-75">
                {features[0].text}
              </p>
            </div>
          </article>
          {features.slice(1).map((feature) => (
            <article
              key={feature.number}
              className={`flex min-h-[300px] flex-col justify-between border-b border-[var(--ink)] p-6 sm:border-r sm:p-8 sm:last:border-r-0 ${feature.tone}`}
            >
              <div className="flex items-start justify-between gap-4">
                <span
                  className={`grid size-10 place-items-center border border-[var(--ink)] font-mono text-[11px] font-bold ${feature.accent}`}
                >
                  {feature.number}
                </span>
                <span className="mt-2 block h-px w-12 bg-current opacity-40" />
              </div>
              <div>
                <h3 className="max-w-[320px] text-[clamp(2.25rem,3.1vw,3.3rem)] font-black leading-[0.92] tracking-[-0.03em]">
                  {feature.title}
                </h3>
                <p className="mt-5 max-w-[350px] text-[clamp(1rem,1.25vw,1.12rem)] leading-[1.45] opacity-70">
                  {feature.text}
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
