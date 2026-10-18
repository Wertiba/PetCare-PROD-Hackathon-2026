import { redirect } from 'next/navigation';

// Early scaffolding page: creating pets and events lives on the dashboard.
export default function Page() {
  redirect('/dashboard');
}
