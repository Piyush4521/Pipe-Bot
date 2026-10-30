import type { FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useTelemetry } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import {
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  OctagonAlert,
  Sliders,
  ShieldAlert,
  Gauge,
  Cpu,
  PowerOff,
} from 'lucide-react';

export const VehiclePage: FC = () => {
  useDocumentTitle('Vehicle Control');
  const { isDemoMode } = useAppMode();
  const { vehicleTelemetry } = useTelemetry();

  return (
    <div className="space-y-6">
      {/* Safety Notice Warning Banner */}
      <div className="p-4 bg-status-warning-bg border border-status-warning-border rounded-sm flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-status-warning shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-bold font-mono uppercase text-industrial-900">
              Hardware Actuation Interlock Active
            </h2>
            {isDemoMode && (
              <Badge variant="brand" isMono className="text-[10px]">
                DEMO MODE (SAFETY LOCKED)
              </Badge>
            )}
          </div>
          <p className="text-xs text-industrial-800 leading-relaxed">
            Controls are disabled until hardware safety and backend communication are validated. No motor commands can be transmitted in prototype or demo modes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Direction & Speed Controls (Strictly Disabled) (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Directional Pad Card */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-brand-orange" />
                  <CardTitle className="text-sm">Propulsion Direction Control</CardTitle>
                </div>
                <Badge variant="outline" isMono className="text-[10px] text-status-warning">
                  Interlocked (Disabled)
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Manual directional navigation and pipeline crawler crawl actuation
              </CardDescription>
            </CardHeader>

            <CardContent className="p-6">
              {/* Industrial D-Pad Layout */}
              <div className="max-w-xs mx-auto flex flex-col items-center gap-3">
                {/* Forward Button */}
                <Button
                  variant="outline"
                  size="lg"
                  disabled
                  className="w-24 h-14 font-mono font-bold text-xs"
                  title="Controls are disabled until hardware safety and backend communication are validated"
                >
                  <div className="flex flex-col items-center">
                    <ArrowUp className="w-4 h-4 mb-0.5" />
                    <span>FORWARD</span>
                  </div>
                </Button>

                {/* Left, E-Stop Center, Right */}
                <div className="flex items-center gap-3 w-full justify-center">
                  <Button
                    variant="outline"
                    size="lg"
                    disabled
                    className="w-24 h-14 font-mono font-bold text-xs"
                    title="Controls are disabled until hardware safety and backend communication are validated"
                  >
                    <div className="flex flex-col items-center">
                      <ArrowLeft className="w-4 h-4 mb-0.5" />
                      <span>LEFT</span>
                    </div>
                  </Button>

                  {/* Stop / Neutral Button */}
                  <Button
                    variant="danger"
                    size="lg"
                    disabled
                    className="w-24 h-14 font-mono font-bold text-xs"
                    title="Controls are disabled until hardware safety and backend communication are validated"
                  >
                    <div className="flex flex-col items-center">
                      <OctagonAlert className="w-4 h-4 mb-0.5" />
                      <span>STOP</span>
                    </div>
                  </Button>

                  <Button
                    variant="outline"
                    size="lg"
                    disabled
                    className="w-24 h-14 font-mono font-bold text-xs"
                    title="Controls are disabled until hardware safety and backend communication are validated"
                  >
                    <div className="flex flex-col items-center">
                      <ArrowRight className="w-4 h-4 mb-0.5" />
                      <span>RIGHT</span>
                    </div>
                  </Button>
                </div>

                {/* Reverse Button */}
                <Button
                  variant="outline"
                  size="lg"
                  disabled
                  className="w-24 h-14 font-mono font-bold text-xs"
                  title="Controls are disabled until hardware safety and backend communication are validated"
                >
                  <div className="flex flex-col items-center">
                    <ArrowDown className="w-4 h-4 mb-0.5" />
                    <span>REVERSE</span>
                  </div>
                </Button>
              </div>

              {/* Speed Slider Section (Disabled) */}
              <div className="mt-8 pt-6 border-t border-industrial-200 space-y-3">
                <div className="flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-2 font-bold text-industrial-800">
                    <Gauge className="w-4 h-4 text-industrial-500" />
                    <span>CRAWL VELOCITY LIMITER:</span>
                  </div>
                  <span className="font-bold text-industrial-400">0% (LOCKED)</span>
                </div>

                <input
                  type="range"
                  min="0"
                  max="100"
                  value="0"
                  disabled
                  className="w-full h-2 bg-industrial-200 rounded-sm appearance-none cursor-not-allowed opacity-50"
                  title="Speed control disabled"
                />

                <div className="flex justify-between text-[11px] font-mono text-industrial-400">
                  <span>0% (Halt)</span>
                  <span>50% (Standard Crawl)</span>
                  <span>100% (Max 0.25 m/s)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Hardware Status & Safety Invariants (5 cols on lg) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Hardware Subsystem State Card */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-industrial-800" />
                  <CardTitle className="text-sm">Actuation Subsystem Status</CardTitle>
                </div>
                <StatusIndicator
                  status={isDemoMode ? 'healthy' : 'offline'}
                  label={isDemoMode ? 'Simulated Active' : 'Offline'}
                  size="sm"
                />
              </div>
            </CardHeader>

            <CardContent className="p-4 space-y-2 text-xs font-mono">
              <div className="flex justify-between py-2 border-b border-industrial-100">
                <span className="text-industrial-600">Motion Controller:</span>
                <span className="font-bold text-industrial-900">
                  ESP32-WROOM-32 ({isDemoMode ? 'Simulated' : 'Not connected'})
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-industrial-100">
                <span className="text-industrial-600">Connection State:</span>
                <span className={isDemoMode ? 'text-status-healthy font-semibold' : 'text-status-warning font-semibold'}>
                  {isDemoMode ? 'Simulated Link' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-industrial-100">
                <span className="text-industrial-600">Motor Driver:</span>
                <span className="text-industrial-800">
                  SmartElex 15D ({isDemoMode ? 'Simulated Standby' : 'Unavailable'})
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-industrial-100">
                <span className="text-industrial-600">Left DC Motor Pair:</span>
                <span className="text-industrial-700">
                  {vehicleTelemetry.leftMotorState.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-industrial-100">
                <span className="text-industrial-600">Right DC Motor Pair:</span>
                <span className="text-industrial-700">
                  {vehicleTelemetry.rightMotorState.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-industrial-600">Emergency Stop Status:</span>
                <span className="text-industrial-700">
                  {vehicleTelemetry.emergencyStopEngaged ? 'ENGAGED' : 'Disengaged (Safety Interlocked)'}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Safety Protocols & Invariants */}
          <Card variant="default" className="border-industrial-200">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <PowerOff className="w-4 h-4 text-status-critical" />
                <CardTitle className="text-xs uppercase font-mono tracking-wider">
                  Mandatory Safety Invariants
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="text-xs text-industrial-600 space-y-2.5 leading-relaxed">
              <div className="p-2.5 bg-industrial-100 border border-industrial-200 rounded-sm">
                <span className="font-mono font-bold text-industrial-900 block mb-0.5">
                  1. Communication Heartbeat Watchdog
                </span>
                <p className="text-[11px] text-industrial-600">
                  Firmware must halt all DC motor PWM channels if no valid command packet is received within 250 milliseconds.
                </p>
              </div>

              <div className="p-2.5 bg-industrial-100 border border-industrial-200 rounded-sm">
                <span className="font-mono font-bold text-industrial-900 block mb-0.5">
                  2. Hard E-Stop Interlock Protocol
                </span>
                <p className="text-[11px] text-industrial-600">
                  Emergency stop takes immediate preemptive priority over any in-flight navigation command sequence.
                </p>
              </div>

              <div className="p-2.5 bg-industrial-100 border border-industrial-200 rounded-sm">
                <span className="font-mono font-bold text-industrial-900 block mb-0.5">
                  3. Overcurrent Fault Cutoff
                </span>
                <p className="text-[11px] text-industrial-600">
                  SmartElex 15D current monitoring shuts down motors when mechanical wheel obstruction causes stall currents.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default VehiclePage;
