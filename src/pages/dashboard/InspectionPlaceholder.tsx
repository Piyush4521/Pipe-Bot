import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const InspectionPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Live Inspection Studio"
        description="Real-time ESP32-CAM video stream, AI defect bounding box overlays, and encoder odometry tracking."
        badge={<Badge variant="default">Stage 4 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Live Inspection Studio"
        routePath={ROUTES.DASHBOARD.INSPECTION}
        targetStage="Stage 4: Live Camera & Vision Interface"
        plannedFeatures={[
          'Real-time low-latency video feed from ESP32-CAM (OV2640)',
          'AI YOLO defect inference bounding boxes with confidence scores',
          'Live distance marker synchronised with wheel encoder pulses',
          'Manual snapshot capture and operator defect bookmarking',
          'Pipeline illumination and camera orientation controls',
        ]}
      />
    </div>
  );
};
