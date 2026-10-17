import {
  FeatureShowcase,
  FinalCTA,
  HeroSection,
  LandingFooter,
  LandingHeader,
  ProductIntro,
} from '@src/widgets/ui/landing-page';

export default function Home() {
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
