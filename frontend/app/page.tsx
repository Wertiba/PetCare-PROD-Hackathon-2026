import Header from '@src/widgets/ui/Header';

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto w-full max-w-5xl px-4 py-16">
        <h1 className="text-4xl font-bold text-black">
          qwerty
        </h1>
        <p className="mt-2 text-xl text-neutral-600">
          team
        </p>
      </main>
    </div>
  );
}
