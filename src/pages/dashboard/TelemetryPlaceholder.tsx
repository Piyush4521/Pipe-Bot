import type { FC } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { RouteVerificationBanner } from '@/components/shared/RouteVerificationBanner';
import { ROUTES } from '@/constants/routes';

export const TelemetryPlaceholder: FC = () => {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Sensor & Encoder Telemetry"
        description="High-resolution time-series sensor logs, optical encoder distance measurements, and battery health."
        badge={<Badge variant="default">Stage 3 Target</Badge>}
      />

      <RouteVerificationBanner
        routeName="Sensor & Encoder Telemetry"
        routePath={ROUTES.DASHBOARD.TELEMETRY}
        targetStage="Stage 3: Telemetry Stream"
        plannedFeatures={[
          'Encoder distance calculation and linear speed tracking',
          'Battery cell voltage, estimated remaining inspection endurance',
          'ESP32 internal junction temperature monitoring',
          'Wi-Fi signal attenuation & packet loss metrics',
          'IMU pitch and roll sensor orientation in pipe bends',
        ]}
      />
    </div>
  );
};
