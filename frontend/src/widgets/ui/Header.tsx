import Link from 'next/link';

import { UserMenu } from './UserMenu';

/**
 * Shared link styles. Two tones exist because some links sit on tinted or
 * dark surfaces elsewhere in the UI; both are neutral in the baseline theme.
 */
export const linkClasses =
  'text-sm text-black hover:underline';

export const whiteLinkClasses =
  'text-sm text-neutral-600 hover:underline';

export default function Header() {
  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex h-12 w-full max-w-5xl items-center gap-6 px-4">
        <Link href="/" className={linkClasses}>
          home
        </Link>
        <Link href="/register" className={linkClasses}>
          register
        </Link>
        <Link href="/login" className={linkClasses}>
          login
        </Link>
        <UserMenu />
      </div>
    </header>
  );
}
