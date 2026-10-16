'use client';

interface SubmitButtonProps {
  pending: boolean;
  pendingLabel: string;
  children: string;
}

export function SubmitButton({
  pending,
  pendingLabel,
  children,
}: SubmitButtonProps) {
  return (
    <button
      type="submit"
      disabled={pending}
      className="mt-2 w-full cursor-pointer rounded bg-black px-4 py-2.5 text-sm font-medium text-white transition-colors enabled:hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {pending ? pendingLabel : children}
    </button>
  );
}
