import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const DefectsPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Defect Records & Classification"
        description="Comprehensive catalogue of detected pipeline defects, AI confidence metrics, and precise distance markers."
        badge={<Badge variant="default">Stage 4 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Defect Classification & Logs"
        routePath={ROUTES.DASHBOARD.DEFECTS}
        targetStage="Stage 4: Defect Analytics & Records"
        plannedFeatures={[
          'Searchable and filterable defect table (cracks, joint displacements, blockages, deformations)',
          'High-resolution snapshot viewer with YOLO inference boxes',
          'Severity grading (minor, moderate, severe, critical)',
          'Manual operator annotation, verification, and false-positive dismissal',
          'Export of defect spatial distribution along the pipeline length',
        ]}
      />
    </div>
  );
};
