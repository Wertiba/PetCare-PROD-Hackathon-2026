import Link from 'next/link';

interface ActionLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  emphasis?: 'default' | 'hero';
}

const emphasisClasses = {
  default:
    'px-7 py-4 text-[0.95rem] shadow-[5px_5px_0_var(--ink)] hover:translate-x-1 hover:translate-y-1 hover:shadow-[2px_2px_0_var(--ink)] focus-visible:outline-[var(--lime)]',
  hero: 'w-fit shrink-0 px-7 py-5 text-base shadow-[6px_6px_0_var(--ink)] hover:translate-x-1 hover:translate-y-1 hover:shadow-[3px_3px_0_var(--ink)] focus-visible:outline-[var(--forest)]',
} as const;

export function ActionLink({
  href,
  children,
  className = '',
  emphasis = 'default',
}: ActionLinkProps) {
  return (
    <Link
      href={href}
      className={`group inline-flex items-center gap-4 border border-[var(--ink)] bg-[var(--lime)] font-bold tracking-[0.01em] text-[var(--forest)] transition-all focus-visible:outline-2 focus-visible:outline-offset-4 ${emphasisClasses[emphasis]} ${className}`}
    >
      {children}
      <span
        aria-hidden="true"
        className="text-lg transition-transform group-hover:translate-x-1"
      >
        →
      </span>
    </Link>
  );
}
