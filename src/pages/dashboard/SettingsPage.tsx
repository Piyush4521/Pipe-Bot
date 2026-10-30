import { useState, type FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { APP_CONFIG } from '@/constants/config';
import {
  Settings,
  Cpu,
  Radio,
  Sliders,
  Sparkles,
  PowerOff,
} from 'lucide-react';

export const SettingsPage: FC = () => {
  useDocumentTitle('System Settings');
  const { mode, setMode, isDemoMode } = useAppMode();

  // Connection parameters
  const [backendUrl, setBackendUrl] = useState(APP_CONFIG.apiBaseUrl);
  const [websocketUrl, setWebsocketUrl] = useState(APP_CONFIG.wsUrl);
  const [cameraStreamUrl, setCameraStreamUrl] = useState(APP_CONFIG.cameraStreamUrl || 'http://192.168.4.1/stream');
  const [measurementUnit, setMeasurementUnit] = useState('metric');
  const [themeMode, setThemeMode] = useState('light-industrial');

  const hardwareSpecs = [
    { label: 'Microcontroller 1', value: 'ESP32-WROOM-32 (Motion, PWM & Interrupts)', status: 'Verified Spec' },
    { label: 'Microcontroller 2', value: 'AI Thinker ESP32-CAM (Optical Module)', status: 'Verified Spec' },
    { label: 'Image Sensor', value: 'OmniVision OV2640 (2.0 Megapixel Sensor)', status: 'Verified Spec' },
    { label: 'Motor Driver', value: 'SmartElex 15D Dual DC Motor Driver', status: 'Verified Spec' },
    { label: 'Inertial Motion Sensor', value: 'MPU6050 6-Axis Accelerometer / Gyroscope', status: 'Verified Spec' },
    { label: 'Rotary Odometry', value: 'Two Optical Quadrature Wheel Encoders', status: 'Verified Spec' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex items-start gap-3">
        <Settings className="w-5 h-5 text-brand-orange shrink-0 mt-0.5" />
        <div className="space-y-0.5 text-xs text-industrial-700 leading-relaxed">
          <span className="font-bold font-mono uppercase text-industrial-900 block">
            System & Hardware Parameters
          </span>
          <p>
            Configure local network routing endpoints, toggle between demonstration and disconnected modes, view planned microcontroller specifications, and adjust application interface preferences.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Network Connection Endpoints & Demo Mode (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Operating Mode Selector Card */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-brand-orange" />
                  <CardTitle className="text-sm">Application Operating Mode</CardTitle>
                </div>
                <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                  {mode.toUpperCase()}
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Switch between disconnected prototype state and controlled demonstration dataset
              </CardDescription>
            </CardHeader>

            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div
                  onClick={() => setMode('disconnected')}
                  className={`p-4 border rounded-sm cursor-pointer transition-colors space-y-1.5 ${
                    mode === 'disconnected'
                      ? 'bg-industrial-900 text-white border-industrial-900 shadow-industrial-sm'
                      : 'bg-white text-industrial-800 border-industrial-300 hover:bg-industrial-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold uppercase">Disconnected Mode</span>
                    <PowerOff className={`w-4 h-4 ${mode === 'disconnected' ? 'text-brand-orange' : 'text-industrial-400'}`} />
                  </div>
                  <p className={`text-[11px] leading-relaxed ${mode === 'disconnected' ? 'text-industrial-300' : 'text-industrial-600'}`}>
                    Genuine empty states with offline indicators. Zero simulated records.
                  </p>
                </div>

                <div
                  onClick={() => setMode('demo')}
                  className={`p-4 border rounded-sm cursor-pointer transition-colors space-y-1.5 ${
                    mode === 'demo'
                      ? 'bg-brand-orange text-white border-brand-orange shadow-industrial-sm'
                      : 'bg-white text-industrial-800 border-industrial-300 hover:bg-industrial-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold uppercase">Demonstration Mode</span>
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <p className={`text-[11px] leading-relaxed ${mode === 'demo' ? 'text-white/90' : 'text-industrial-600'}`}>
                    Populates isolated sample records (odometry, IMU, 4 defect classes) for testing.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Network Routing Endpoints Card */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Radio className="w-4 h-4 text-brand-orange" />
                  <CardTitle className="text-sm">Network Routing Endpoints</CardTitle>
                </div>
                <Badge variant="outline" isMono className="text-[10px]">
                  Local Loopback Target
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Prepared routing configuration for Python FastAPI and ESP32 stream integration
              </CardDescription>
            </CardHeader>

            <CardContent className="p-5 space-y-4">
              <Input
                label="Python FastAPI REST Base URL"
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                helperText="HTTP endpoint for inspection run logs, defect registries, and reports (Stage 5 target)."
              />

              <Input
                label="Asynchronous WebSocket Telemetry Stream URL"
                value={websocketUrl}
                onChange={(e) => setWebsocketUrl(e.target.value)}
                helperText="Sub-millisecond duplex WebSocket protocol for encoder pulses and IMU readings."
              />

              <Input
                label="ESP32-CAM MJPEG Video Stream URL"
                value={cameraStreamUrl}
                onChange={(e) => setCameraStreamUrl(e.target.value)}
                helperText="Direct optical video feed URL broadcasted by the AI Thinker ESP32-CAM module."
              />

              <div className="pt-2 flex items-center justify-between border-t border-industrial-100 text-xs">
                <div className="flex items-center gap-2 text-industrial-500 font-mono text-[11px]">
                  <StatusIndicator status="offline" size="sm" />
                  <span>Connection Testing: Dormant until backend launch</span>
                </div>

                <Button variant="secondary" size="sm" disabled>
                  Test Connection
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Application & Display Preferences */}
          <Card variant="default" className="border-industrial-200">
            <CardHeader className="pb-3 border-b border-industrial-100">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-industrial-800" />
                <CardTitle className="text-sm">Application Interface Preferences</CardTitle>
              </div>
            </CardHeader>

            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="Measurement Units"
                  value={measurementUnit}
                  onChange={(e) => setMeasurementUnit(e.target.value)}
                  options={[
                    { label: 'Metric (Meters, mm, m/s)', value: 'metric' },
                    { label: 'Imperial (Feet, inches, ft/s)', value: 'imperial', disabled: true },
                  ]}
                  helperText="Primary pipeline distance & diameter units."
                />

                <Select
                  label="Dashboard Theme Palette"
                  value={themeMode}
                  onChange={(e) => setThemeMode(e.target.value)}
                  options={[
                    { label: 'Light Industrial (High Contrast)', value: 'light-industrial' },
                    { label: 'Dark Industrial (Planned)', value: 'dark-industrial', disabled: true },
                  ]}
                  helperText="Light industrial aesthetic with crisp borders."
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Hardware Target Specifications (Read-Only) (5 cols on lg) */}
        <div className="lg:col-span-5 space-y-6">
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-industrial-900" />
                  <CardTitle className="text-sm">Hardware Configuration Registry</CardTitle>
                </div>
                <Badge variant="outline" isMono className="text-[10px]">
                  Read-Only
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Physical embedded payload specifications for the PipeBot crawler
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 space-y-3 font-mono text-xs">
              {hardwareSpecs.map((spec) => (
                <div key={spec.label} className="p-2.5 bg-industrial-50 border border-industrial-200 rounded-sm">
                  <div className="flex items-center justify-between text-industrial-500 text-[11px] mb-0.5">
                    <span>{spec.label}</span>
                    <span className="text-status-healthy font-semibold">{spec.status}</span>
                  </div>
                  <div className="font-bold text-industrial-900 text-xs">
                    {spec.value}
                  </div>
                </div>
              ))}

              <div className="p-3 bg-industrial-100 border border-industrial-200 rounded-sm text-[11px] text-industrial-600 font-sans leading-relaxed">
                Calibration Notice: Wheel diameter and encoder ticks-per-revolution (PPR) constants are not hardcoded. Calibration routines will execute during hardware commissioning.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
