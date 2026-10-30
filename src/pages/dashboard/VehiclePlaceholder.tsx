import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const VehiclePlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Vehicle Control Interface"
        description="Crawler propulsion control, speed calibration, emergency stop triggers, and motor diagnostics."
        badge={<Badge variant="default">Stage 4 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Vehicle Propulsion & Control"
        routePath={ROUTES.DASHBOARD.VEHICLE}
        targetStage="Stage 4: Vehicle Control & Actuation"
        plannedFeatures={[
          'Forward, reverse, and crawl velocity regulation',
          'Hardware emergency stop (E-STOP) trigger protocol',
          'Dual DC motor driver status and current draw indicators',
          'Encoder pulse synchronization and calibration utility',
          'Traction control and pipeline obstacle recovery toggles',
        ]}
      />
    </div>
  );
};
