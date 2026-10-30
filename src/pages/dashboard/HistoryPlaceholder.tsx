import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const HistoryPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Inspection History & Archive"
        description="Historical log of past pipeline inspection runs, defect trends, and mission replays."
        badge={<Badge variant="default">Stage 4 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Inspection Mission History"
        routePath={ROUTES.DASHBOARD.HISTORY}
        targetStage="Stage 4: Mission Archives"
        plannedFeatures={[
          'Chronological log of past inspection runs with pipe IDs and timestamps',
          'Defect comparison across multi-year re-inspections of the same pipeline segment',
          'Complete telemetry replay of vehicle runs',
          'Filter by pipe location, inspector ID, and defect count',
        ]}
      />
    </div>
  );
};
