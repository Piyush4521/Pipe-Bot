import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const ReportsPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Inspection Reports & Compliance"
        description="Automated engineering inspection reports, executive summaries, and standard compliance exports."
        badge={<Badge variant="default">Stage 5 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Automated Inspection Reports"
        routePath={ROUTES.DASHBOARD.REPORTS}
        targetStage="Stage 5: Reports & Backend Integration"
        plannedFeatures={[
          'One-click PDF generation with defect imagery and distance markers',
          'Executive summary of pipeline condition rating',
          'CSV / JSON telemetry and defect data exports',
          'Sign-off digital signature workflow for certified pipeline inspectors',
        ]}
      />
    </div>
  );
};