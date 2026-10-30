import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const DashboardOverviewPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Inspection Dashboard Overview"
        description="Centralized operational console aggregating live mission state, recent defects, and hardware telemetry."
        badge={<Badge variant="default">Stage 3 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Dashboard Overview"
        routePath={ROUTES.DASHBOARD.ROOT}
        targetStage="Stage 3: Core Dashboard & Telemetry"
        plannedFeatures={[
          'Active pipeline run status and distance traversed',
          'Live defect count categorized by severity',
          'Hardware communication heartbeat monitor',
          'Recent inspection runs list and quick-resume controls',
          'Environmental telemetry cards (battery, internal temperature, Wi-Fi RSSI)',
        ]}
      />
    </div>
  );
};
