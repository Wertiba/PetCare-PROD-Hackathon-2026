'use client';

import {
  selectUser,
  useUserStore,
} from '@src/entities/user';

function getInitials(fullName: string | undefined) {
  const initials = fullName
    ?.trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('');

  return initials || 'P';
}

/** A persistent account summary that deliberately uses the API-backed user store. */
export function AccountProfileCard() {
  const user = useUserStore(selectUser);
  const fullName = user?.fullName || 'Профиль PetCare';
  const login = user?.login || 'user';

  return (
    <section
      aria-labelledby="profile-card-heading"
      className="mt-7 overflow-hidden rounded-md border-2 border-[var(--forest)] bg-[var(--forest)] text-white shadow-[6px_6px_0_var(--lime)]"
    >
      <div className="flex flex-col gap-5 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
        <div className="flex min-w-0 items-center gap-4">
          <span
            aria-hidden="true"
            className="grid size-16 shrink-0 place-items-center rounded-full border-2 border-[var(--lime)] bg-white text-xl font-black text-[var(--forest)] shadow-[3px_3px_0_rgba(255,255,255,.2)]"
          >
            {getInitials(user?.fullName)}
          </span>
          <div className="min-w-0">
            <p className="text-xs font-bold tracking-[.14em] text-[var(--lime)] uppercase">
              Мой профиль
            </p>
            <h2
              id="profile-card-heading"
              className="mt-1 truncate text-2xl font-black"
            >
              {fullName}
            </h2>
            <p className="mt-1 truncate text-sm font-semibold text-white/70">
              @{login}
            </p>
          </div>
        </div>
        <span className="inline-flex w-fit items-center gap-2 rounded-sm border border-white/25 bg-white/10 px-3 py-2 text-sm font-bold text-white/85">
          <span
            aria-hidden="true"
            className="size-2 rounded-full bg-[var(--lime)]"
          />
          Аккаунт активен
        </span>
      </div>
    </section>
  );
}
