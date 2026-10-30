import type { FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { LandingNavbar } from './components/LandingNavbar';
import { HeroSection } from './components/HeroSection';
import { PlatformOverview } from './components/PlatformOverview';
import { WorkflowSection } from './components/WorkflowSection';
import { ArchitectureSection } from './components/ArchitectureSection';
import { DefectCapabilities } from './components/DefectCapabilities';
import { LocalizationSection } from './components/LocalizationSection';
import { TechnologySection } from './components/TechnologySection';
import { FinalCTA } from './components/FinalCTA';
import { LandingFooter } from './components/LandingFooter';

export const LandingPage: FC = () => {
  useDocumentTitle('Intelligent Pipeline Inspection');

  return (
    <div className="min-h-screen flex flex-col bg-industrial-50 text-industrial-900 selection:bg-brand-orange selection:text-white">
      {/* Section A: Navigation */}
      <LandingNavbar />

      <main className="flex-1">
        {/* Section B: Hero */}
        <HeroSection />

        {/* Section C: Platform Overview */}
        <PlatformOverview />

        {/* Section D: Inspection Process / Workflow */}
        <WorkflowSection />

        {/* Section E: Technical Architecture */}
        <ArchitectureSection />

        {/* Section F: Target Defect Classifications */}
        <DefectCapabilities />

        {/* Section G: Inspection Data & Spatial Localization */}
        <LocalizationSection />

        {/* Section H: Technology Stack & Layering */}
        <TechnologySection />

        {/* Section I: Final Call To Action */}
        <FinalCTA />
      </main>

      {/* Section J: Global Landing Footer */}
      <LandingFooter />
    </div>
  );
};

export default LandingPage;

