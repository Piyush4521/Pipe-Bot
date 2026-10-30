import type { FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useTelemetry } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  Activity,
  Ruler,
  Compass,
  LineChart,
  Gauge,
  Radio,
} from 'lucide-react';

export const TelemetryPage: FC = () => {
  useDocumentTitle('Odometry & Telemetry');
  const { isDemoMode } = useAppMode();
  const { encoderTelemetry, imuTelemetry } = useTelemetry();

  const encoderMetrics = [
    {
      label: 'Left Encoder Ticks',
      value: encoderTelemetry.leftTicks !== null ? `${encoderTelemetry.leftTicks.toLocaleString()} pulses` : 'Awaiting telemetry',
      unit: 'pulses',
    },
    {
      label: 'Right Encoder Ticks',
      value: encoderTelemetry.rightTicks !== null ? `${encoderTelemetry.rightTicks.toLocaleString()} pulses` : 'Awaiting telemetry',
      unit: 'pulses',
    },
    {
      label: 'Left Wheel RPM',
      value: encoderTelemetry.leftRpm !== null ? `${encoderTelemetry.leftRpm.toFixed(1)} RPM` : 'Awaiting telemetry',
      unit: 'rev/min',
    },
    {
      label: 'Right Wheel RPM',
      value: encoderTelemetry.rightRpm !== null ? `${encoderTelemetry.rightRpm.toFixed(1)} RPM` : 'Awaiting telemetry',
      unit: 'rev/min',
    },
    {
      label: 'Estimated Traversal',
      value: encoderTelemetry.estimatedDistanceMeters !== null ? `${encoderTelemetry.estimatedDistanceMeters.toFixed(2)} m` : 'Awaiting telemetry',
      unit: 'meters',
    },
  ];

  const imuMetrics = [
    {
      axis: 'X',
      accel: imuTelemetry.accelX !== null ? `${imuTelemetry.accelX.toFixed(2)} g` : 'Awaiting telemetry',
      gyro: imuTelemetry.gyroX !== null ? `${imuTelemetry.gyroX.toFixed(1)} °/s` : 'Awaiting telemetry',
    },
    {
      axis: 'Y',
      accel: imuTelemetry.accelY !== null ? `${imuTelemetry.accelY.toFixed(2)} g` : 'Awaiting telemetry',
      gyro: imuTelemetry.gyroY !== null ? `${imuTelemetry.gyroY.toFixed(1)} °/s` : 'Awaiting telemetry',
    },
    {
      axis: 'Z',
      accel: imuTelemetry.accelZ !== null ? `${imuTelemetry.accelZ.toFixed(2)} g` : 'Awaiting telemetry',
      gyro: imuTelemetry.gyroZ !== null ? `${imuTelemetry.gyroZ.toFixed(1)} °/s` : 'Awaiting telemetry',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Telemetry Status Strip */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
            <Radio className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold uppercase text-industrial-900">
                Telemetry Link Status:
              </span>
              <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                {isDemoMode ? 'SIMULATED TELEMETRY' : 'Port 8000 /ws Dormant'}
              </Badge>
            </div>
            <p className="text-xs text-industrial-600 mt-0.5">
              {isDemoMode
                ? 'Rendering simulated encoder odometry pulses and IMU pitch/roll readings.'
                : 'Live sensor streams will populate below when ESP32 telemetry broadcast connects to the local WebSocket server.'}
            </p>
          </div>
        </div>

        <StatusIndicator
          status={isDemoMode ? 'healthy' : 'offline'}
          label={isDemoMode ? 'Simulated Active' : 'Sensor Link Offline'}
          size="sm"
        />
      </div>

      {/* 1. Encoder Odometry Cards Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Ruler className="w-4 h-4 text-brand-orange" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-900 font-mono">
              Rotary Encoder Odometry
            </h2>
          </div>
          <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
            {isDemoMode ? 'DEMO DATA' : 'Dual Optical Channels'}
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {encoderMetrics.map((metric) => (
            <Card key={metric.label} variant="raised" className="border-industrial-300">
              <CardHeader className="p-4 pb-1">
                <CardDescription className="font-mono text-[11px] text-industrial-500 uppercase">
                  {metric.label}
                </CardDescription>
                <div className={`text-sm font-mono font-bold mt-1 ${isDemoMode ? 'text-industrial-900' : 'text-industrial-400'}`}>
                  {metric.value}
                </div>
              </CardHeader>
              <CardContent className="p-4 pt-1 text-[11px] font-mono text-industrial-400">
                Unit: {metric.unit}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* 2. MPU6050 Motion Tracking & Mathematical Formulation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* MPU6050 Accelerometer & Gyroscope (6 cols on lg) */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-industrial-900" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-900 font-mono">
              MPU6050 6-Axis Motion Sensor
            </h2>
          </div>

          <Card variant="default" className="border-industrial-200 overflow-hidden">
            <div className="p-3 bg-industrial-100 border-b border-industrial-200 flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-industrial-800">Inertial Measurement Units</span>
              <span className="text-industrial-500">I2C Address: 0x68</span>
            </div>

            <div className="p-4 space-y-3">
              <div className="grid grid-cols-3 gap-3 text-center text-xs font-mono">
                {imuMetrics.map((m) => (
                  <div key={m.axis} className="p-3 bg-industrial-50 border border-industrial-200 rounded-sm space-y-1">
                    <span className="font-bold text-industrial-900 block text-sm">Axis {m.axis}</span>
                    <div className="text-[11px] text-industrial-500">
                      Accel: <span className={isDemoMode ? 'text-industrial-900 font-bold' : 'text-industrial-400'}>{m.accel}</span>
                    </div>
                    <div className="text-[11px] text-industrial-500">
                      Gyro: <span className={isDemoMode ? 'text-industrial-900 font-bold' : 'text-industrial-400'}>{m.gyro}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-3 bg-industrial-50 border border-industrial-200 rounded-sm text-xs font-mono flex items-center justify-between">
                <span className="text-industrial-600">Conduit Incline / Pitch Angle:</span>
                <span className={`font-bold ${isDemoMode ? 'text-brand-orange' : 'text-industrial-400'}`}>
                  {imuTelemetry.pitchDegrees !== null ? `${imuTelemetry.pitchDegrees > 0 ? '+' : ''}${imuTelemetry.pitchDegrees.toFixed(1)}°` : 'Awaiting telemetry'}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Mathematical Distance Formulation (6 cols on lg) */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center gap-2">
            <Gauge className="w-4 h-4 text-industrial-900" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-900 font-mono">
              Distance Estimation Formulation
            </h2>
          </div>

          <Card variant="default" className="border-industrial-200">
            <CardHeader className="pb-2 border-b border-industrial-100">
              <CardTitle className="text-xs uppercase font-mono tracking-wider">
                Rotary Integration Mathematical Model
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3 text-xs text-industrial-700 leading-relaxed font-mono">
              <div className="p-3 bg-industrial-100 border border-industrial-200 rounded-sm space-y-1 text-center">
                <div className="text-industrial-600 text-[11px]">Wheel Circumference:</div>
                <div className="font-bold text-industrial-900 text-sm">C = π × wheel diameter</div>
              </div>

              <div className="p-3 bg-industrial-100 border border-industrial-200 rounded-sm space-y-1 text-center">
                <div className="text-industrial-600 text-[11px]">Channel Travel Distance:</div>
                <div className="font-bold text-industrial-900 text-sm">D = (Pulses / Pulses per wheel revolution) × C</div>
              </div>

              <div className="p-3 bg-industrial-100 border border-industrial-200 rounded-sm space-y-1 text-center">
                <div className="text-industrial-600 text-[11px]">Average Longitudinal Traversal:</div>
                <div className="font-bold text-brand-orange text-sm">Davg = (Dleft + Dright) / 2</div>
              </div>

              <div className="pt-2 text-[11px] text-industrial-500 font-sans">
                Note: Physical wheel diameter and encoder resolution parameters will be calibrated against physical chassis specifications during hardware setup.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 3. Sensor Time-Series Chart Containers */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LineChart className="w-4 h-4 text-industrial-900" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-900 font-mono">
              Telemetry Time-Series Streams
            </h2>
          </div>
          <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
            {isDemoMode ? 'DEMO CHART PREVIEW' : 'Chart Buffer Inactive'}
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Chart 1: Distance over Time Container */}
          <Card variant="default" className="border-industrial-200">
            <CardHeader className="p-4 pb-2 border-b border-industrial-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs uppercase font-mono">Linear Traversal (Distance vs. Time)</CardTitle>
                <CardDescription className="text-xs">Continuous encoder integration curve</CardDescription>
              </div>
              <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
                {isDemoMode ? 'Demo Vector: 14.52m' : '0 Data Points'}
              </Badge>
            </CardHeader>
            <CardContent className="p-6">
              {isDemoMode || encoderTelemetry.estimatedDistanceMeters !== null ? (
                <div className="p-4 bg-industrial-50 border border-industrial-200 rounded-sm space-y-3 font-mono text-xs">
                  <div className="flex justify-between text-industrial-600">
                    <span>Odometry Integration:</span>
                    <span className="font-bold text-industrial-900">
                      {encoderTelemetry.estimatedDistanceMeters != null
                        ? `${encoderTelemetry.estimatedDistanceMeters.toFixed(2)} m`
                        : '0.00 m'}
                    </span>
                  </div>
                  <div className="w-full bg-industrial-200 h-2 rounded-sm overflow-hidden">
                    <div
                      className="bg-brand-orange h-full transition-all duration-300"
                      style={{
                        width: `${Math.min(
                          ((encoderTelemetry.estimatedDistanceMeters ?? 0) / 20) * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-industrial-500">
                    <span>Entry Point (0.00 m)</span>
                    <span className="text-brand-orange font-bold">
                      Current: {(encoderTelemetry.estimatedDistanceMeters ?? 0).toFixed(2)} m
                    </span>
                    <span>Range: 20.00 m</span>
                  </div>
                </div>
              ) : (
                <EmptyState
                  icon={<Activity className="w-6 h-6 text-industrial-400" />}
                  title="Awaiting Distance Telemetry"
                  description="Real-time odometry curves will plot distance accumulation here once the crawler starts traversing the pipeline."
                />
              )}
            </CardContent>
          </Card>

          {/* Chart 2: Incline & Pitch Profile Container */}
          <Card variant="default" className="border-industrial-200">
            <CardHeader className="p-4 pb-2 border-b border-industrial-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs uppercase font-mono">Conduit Slope (Pitch Angle vs. Distance)</CardTitle>
                <CardDescription className="text-xs">MPU6050 incline measurement across pipe joints</CardDescription>
              </div>
              <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
                {imuTelemetry.pitchDegrees != null
                  ? `Pitch: ${imuTelemetry.pitchDegrees.toFixed(1)}°`
                  : '0 Data Points'}
              </Badge>
            </CardHeader>
            <CardContent className="p-6">
              {isDemoMode || imuTelemetry.pitchDegrees !== null ? (
                <div className="p-4 bg-industrial-50 border border-industrial-200 rounded-sm space-y-3 font-mono text-xs">
                  <div className="flex justify-between text-industrial-600">
                    <span>Gradient Trend:</span>
                    <span className="font-bold text-status-healthy">
                      Incline Angle: {(imuTelemetry.pitchDegrees ?? 0).toFixed(1)}°
                    </span>
                  </div>
                  <div className="w-full bg-industrial-200 h-2 rounded-sm overflow-hidden flex">
                    <div
                      className="bg-status-healthy h-full transition-all duration-300"
                      style={{
                        width: `${Math.min(
                          Math.abs(imuTelemetry.pitchDegrees ?? 0) * 10,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-industrial-500">
                    <span>Roll: {(imuTelemetry.rollDegrees ?? 0).toFixed(1)}°</span>
                    <span className="text-industrial-900 font-bold">
                      Pitch: {(imuTelemetry.pitchDegrees ?? 0).toFixed(1)}°
                    </span>
                    <span>Gravity Axis: Z</span>
                  </div>
                </div>
              ) : (
                <EmptyState
                  icon={<Compass className="w-6 h-6 text-industrial-400" />}
                  title="Awaiting IMU Orientation"
                  description="Conduit grade changes and vertical joint drops will render here based on accelerometer fusion."
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TelemetryPage;
