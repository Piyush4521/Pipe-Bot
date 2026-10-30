import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const LandingPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="PipeBot Public Landing"
        description="Public product portal, system overview, and industrial inspection capabilities showcase."
        badge={<Badge variant="brand">Stage 2 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Public Landing Portal"
        routePath={ROUTES.HOME}
        targetStage="Stage 2: Public Landing Page"
        plannedFeatures={[
          'Editorial hero section with industrial pipeline graphics',
          'Robotic inspection architecture overview',
          'AI YOLO defect classification feature highlights',
          'Dual optical encoder distance estimation overview',
          'Technical hardware specifications summary (ESP32-WROOM-32 & ESP32-CAM)',
          'Automated inspection report generation preview',
        ]}
      />
    </div>
  );
};
