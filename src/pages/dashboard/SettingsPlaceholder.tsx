import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const SettingsPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="System & Hardware Configuration"
        description="ESP32 hardware connection parameters, camera resolutions, wheel calibration constants, and model thresholds."
        badge={<Badge variant="default">Stage 5 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="System & Hardware Settings"
        routePath={ROUTES.DASHBOARD.SETTINGS}
        targetStage="Stage 5: Hardware Settings & Backend Wiring"
        plannedFeatures={[
          'ESP32-WROOM-32 IP address, port, and WebSocket endpoint configuration',
          'ESP32-CAM stream resolution, frame rate, and brightness settings',
          'Wheel diameter and encoder ticks-per-meter calibration settings',
          'AI YOLO defect confidence threshold adjustments',
          'Python FastAPI backend base URL and authentication tokens',
        ]}
      />
    </div>
  );
};
