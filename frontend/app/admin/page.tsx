import { Admin } from '@src/widgets';
import { Suspense } from 'react';

interface AdminPageProps {
  searchParams: Promise<{ tab?: string }>;
}

export default function AdminPage({
  searchParams,
}: AdminPageProps) {
  return (
    <Suspense fallback={<Admin activeTab="animals" />}>
      <AdminContent searchParams={searchParams} />
    </Suspense>
  );
}

async function AdminContent({
  searchParams,
}: AdminPageProps) {
  const { tab } = await searchParams;
  const activeTab =
    tab === 'breeds' || tab === 'categories'
      ? tab
      : 'animals';

  return <Admin activeTab={activeTab} />;
}
