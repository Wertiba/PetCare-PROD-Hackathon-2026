'use client';

import {
  selectIsSessionRestored,
  selectUser,
  useUserStore,
} from '@src/entities/user';
import {
  FeatureShowcase,
  FinalCTA,
  HeroSection,
  LandingFooter,
  LandingHeader,
  ProductIntro,
} from '@src/widgets/ui/landing-page';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const router = useRouter();
  const user = useUserStore(selectUser);
  const isSessionRestored = useUserStore(
    selectIsSessionRestored,
  );

  useEffect(() => {
    if (isSessionRestored && user) {
      router.replace('/dashboard');
    }
  }, [isSessionRestored, router, user]);

  if (!isSessionRestored || user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-(--cream) text-(--ink)">
      <LandingHeader />
      <main>
        <HeroSection />
        <ProductIntro />
        <FeatureShowcase />
        <FinalCTA />
      </main>
      <LandingFooter />
    </div>
  );
}
