import { Account } from '@src/widgets';
import { Suspense } from 'react';

interface AccountPageProps {
  searchParams: Promise<{ tab?: string }>;
}

export default function AccountPage({
  searchParams,
}: AccountPageProps) {
  return (
    <Suspense fallback={<Account activeTab="settings" />}>
      <AccountContent searchParams={searchParams} />
    </Suspense>
  );
}

async function AccountContent({
  searchParams,
}: AccountPageProps) {
  const { tab } = await searchParams;
  const activeTab =
    tab === 'calendar' ? 'calendar' : 'settings';

  return <Account activeTab={activeTab} />;
}
