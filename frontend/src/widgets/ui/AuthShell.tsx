import Header from './Header';

interface AuthShellProps {
  title: string;
  children: React.ReactNode;
}

/** Shared layout for the auth pages: header plus a centered plain panel. */
export function AuthShell({
  title,
  children,
}: AuthShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-md border border-neutral-200 bg-white p-8 sm:p-10">
          <h1 className="mb-6 text-xl font-semibold lowercase">
            {title}
          </h1>
          {children}
        </div>
      </main>
    </div>
  );
}
