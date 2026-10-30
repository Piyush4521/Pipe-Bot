import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useInspection } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import {
  Eye,
  Sliders,
  AlertOctagon,
  History,
  FileText,
  Activity,
  ArrowRight,
  Cpu,
  Camera,
  Server,
  Layers,
  Inbox,
  AlertTriangle,
} from 'lucide-react';

export const OverviewPage: FC = () => {
  useDocumentTitle('Console Overview');
  const { isDemoMode } = useAppMode();
  const { inspections } = useInspection();

  const subsystemStates = [
    {
      name: 'Hardware Controller',
      device: 'ESP32-WROOM-32',
      status: (isDemoMode ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isDemoMode ? 'Simulated Active' : 'Not connected',
      note: isDemoMode ? 'Simulated dual encoder odometry' : 'Awaiting local Wi-Fi / Serial link',
      icon: Cpu,
    },
    {
      name: 'Optical Camera',
      device: 'AI Thinker ESP32-CAM',
      status: 'offline' as const, // Camera remains disconnected even in demo mode
      label: 'Not connected',
      note: 'MJPEG video stream unavailable',
      icon: Camera,
    },
    {
      name: 'AI Inference Server',
      device: 'Ultralytics YOLO (PyTorch)',
      status: (isDemoMode ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isDemoMode ? 'Model Ready (Demo)' : 'Not connected',
      note: isDemoMode ? 'Evaluated 4 dataset anomaly classes' : 'Edge vision pipeline dormant',
      icon: Layers,
    },
    {
      name: 'Processing Backend',
      device: 'Python FastAPI Engine',
      status: (isDemoMode ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isDemoMode ? 'Simulated Broker' : 'Not connected',
      note: isDemoMode ? 'Dispatching simulated odometry packets' : 'REST & WebSocket broker unlinked',
      icon: Server,
    },
  ];

  const quickActionCards = [
    {
      title: 'Live Inspection',
      description: 'Access the real-time video viewport, anomaly reticles, and session controls.',
      path: ROUTES.DASHBOARD.INSPECTION,
      icon: Eye,
      badge: 'Capture',
    },
    {
      title: 'Vehicle Propulsion',
      description: 'Review drive motor status, speed limits, and hardware safety interlocks.',
      path: ROUTES.DASHBOARD.VEHICLE,
      icon: Sliders,
      badge: 'Mobility',
    },
    {
      title: 'Sensor Telemetry',
      description: 'Monitor dual rotary encoder pulse counts, estimated distance, and IMU data.',
      path: ROUTES.DASHBOARD.TELEMETRY,
      icon: Activity,
      badge: 'Odometry',
    },
    {
      title: 'Defect Catalogue',
      description: 'View recorded pipeline anomalies classified by type, severity, and location.',
      path: ROUTES.DASHBOARD.DEFECTS,
      icon: AlertOctagon,
      badge: 'Defects',
    },
    {
      title: 'Mission History',
      description: 'Review completed pipeline inspection archives and historical conduit runs.',
      path: ROUTES.DASHBOARD.HISTORY,
      icon: History,
      badge: 'Archives',
    },
    {
      title: 'Inspection Reports',
      description: 'Inspect compliance logs and prepare automated summary reports.',
      path: ROUTES.DASHBOARD.REPORTS,
      icon: FileText,
      badge: 'Reporting',
    },
  ];

  const architectureSubsystems = [
    { name: 'ESP32-WROOM-32', role: 'Motion PWM & Interrupts', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'ESP32-CAM (OV2640)', role: 'Optical Pipeline Video', state: 'Planned / Unlinked' },
    { name: 'SmartElex 15D Driver', role: 'Dual H-Bridge Motor Control', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: '4x DC Geared Motors', role: 'Crawler 4WD Propulsion', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'Dual Optical Encoders', role: 'Rotary Odometry Ticks', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'MPU6050 6-Axis IMU', role: 'Incline & Roll Angle Tracking', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'Python FastAPI Server', role: 'Telemetry Broker & API Hub', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'Ultralytics YOLO Head', role: 'Anomaly Computer Vision', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
    { name: 'SQLite Storage Layer', role: 'Local Inspection Database', state: isDemoMode ? 'Simulated' : 'Planned / Unlinked' },
  ];

  return (
    <div className="space-y-8">
      {/* Prototype Status Notification Banner */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold uppercase text-industrial-900">
                System Mode: {isDemoMode ? 'Demonstration Mode' : 'Engineering Prototype'}
              </span>
              <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                {isDemoMode ? 'Simulated Hardware' : 'Hardware Disconnected'}
              </Badge>
            </div>
            <p className="text-xs text-industrial-600">
              {isDemoMode
                ? 'Previewing dashboard with representative sample records. Motor commands remain disabled.'
                : 'The dashboard interface is operational. All hardware endpoints and live streaming channels remain inactive until backend integration.'}
            </p>
          </div>
        </div>

        <NavLink to={ROUTES.DASHBOARD.INSPECTION} className="shrink-0">
          <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
            Start Inspection Session
          </Button>
        </NavLink>
      </div>

      {/* 1. Subsystem Connection Status Panel */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
            Subsystem Link Matrix
          </h2>
          <span className="text-xs font-mono text-industrial-500">
            {isDemoMode ? '3 / 4 Subsystems Simulated' : '0 / 4 Subsystems Online'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {subsystemStates.map((subsystem) => {
            const Icon = subsystem.icon;
            return (
              <Card key={subsystem.name} variant="default" className="border-industrial-200">
                <CardHeader className="p-4 pb-2 border-b border-industrial-100">
                  <div className="flex items-center justify-between">
                    <div className="p-1.5 bg-industrial-100 text-industrial-700 rounded-sm">
                      <Icon className="w-4 h-4" />
                    </div>
                    <StatusIndicator status={subsystem.status} label={subsystem.label} size="sm" />
                  </div>
                  <CardTitle className="text-xs font-bold text-industrial-900 mt-2">
                    {subsystem.name}
                  </CardTitle>
                  <CardDescription className="font-mono text-[11px] text-industrial-500">
                    {subsystem.device}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-2 text-[11px] font-mono text-industrial-500">
                  {subsystem.note}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 2. Main Feature Quick Access Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
          Operator Console Modules
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActionCards.map((card) => {
            const Icon = card.icon;
            return (
              <Card key={card.title} variant="raised" className="border-industrial-200 flex flex-col justify-between hover:border-industrial-400 transition-colors">
                <CardHeader className="p-5 pb-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm">
                      <Icon className="w-4 h-4" />
                    </div>
                    <Badge variant="default" isMono className="text-[10px]">
                      {card.badge}
                    </Badge>
                  </div>
                  <CardTitle className="text-sm mt-3">{card.title}</CardTitle>
                  <CardDescription className="text-xs leading-relaxed mt-1">
                    {card.description}
                  </CardDescription>
                </CardHeader>

                <div className="p-4 pt-0">
                  <NavLink to={card.path}>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-between"
                      rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                    >
                      Open Module
                    </Button>
                  </NavLink>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 3. System Architecture Summary & Recent Inspections (Bento Layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Subsystems Status Table (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
            Subsystem Hardware & Software Architecture
          </h2>

          <Card variant="default" className="border-industrial-200 overflow-hidden">
            <div className="p-4 bg-industrial-100 border-b border-industrial-200 flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-industrial-800 uppercase">
                Subsystem Registry
              </span>
              <Badge variant="outline" isMono className="text-[10px] bg-white">
                {isDemoMode ? 'Demo Active' : 'Stage 4 Spec'}
              </Badge>
            </div>

            <div className="divide-y divide-industrial-100 text-xs font-mono">
              {architectureSubsystems.map((item, idx) => (
                <div key={idx} className="p-3 px-4 flex items-center justify-between hover:bg-industrial-50 transition-colors">
                  <div>
                    <span className="font-bold text-industrial-900 block">{item.name}</span>
                    <span className="text-[11px] text-industrial-500">{item.role}</span>
                  </div>
                  <Badge
                    variant={item.state === 'Simulated' ? 'brand' : 'outline'}
                    isMono
                    className="text-[10px]"
                  >
                    {item.state}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Recent Inspection Runs: Switches dynamically between genuine Empty State and Demo Record */}
        <div className="lg:col-span-5 space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
            Recent Inspection Runs
          </h2>

          <Card variant="default" className="border-industrial-200">
            {inspections.length > 0 ? (
              <div className="p-5 space-y-3 font-mono">
                <div className="flex items-center justify-between border-b border-industrial-100 pb-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="brand" isMono className="text-[10px]">
                      DEMO RECORD
                    </Badge>
                    <span className="font-bold text-xs text-industrial-900">
                      {inspections[0]?.inspectionId}
                    </span>
                  </div>
                  <Badge variant="healthy" isMono className="text-[10px]">
                    {inspections[0]?.status.toUpperCase()}
                  </Badge>
                </div>

                <div className="text-xs space-y-1.5 text-industrial-700">
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Conduit ID:</span>
                    <span className="font-bold">{inspections[0]?.pipeIdentifier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Diameter:</span>
                    <span>{inspections[0]?.pipeDiameterMm} mm PVC</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Total Traversed:</span>
                    <span className="font-bold text-brand-orange">{inspections[0]?.totalDistanceMeters.toFixed(2)} m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Defects Logged:</span>
                    <span className="font-bold text-status-critical">{inspections[0]?.defectCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Completed At:</span>
                    <span className="text-[11px] text-industrial-500">{inspections[0]?.completedAt}</span>
                  </div>
                </div>

                <div className="pt-2 border-t border-industrial-100">
                  <NavLink to={ROUTES.DASHBOARD.HISTORY} className="w-full block">
                    <Button variant="outline" size="sm" className="w-full text-xs">
                      View In History
                    </Button>
                  </NavLink>
                </div>
              </div>
            ) : (
              <EmptyState
                icon={<Inbox className="w-8 h-8 text-industrial-400" />}
                title="No inspections recorded yet."
                description="Once the crawler initiates an inspection run, captured conduit data and defect records will appear in this log."
                action={
                  <NavLink to={ROUTES.DASHBOARD.INSPECTION}>
                    <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                      Open Live Inspection
                    </Button>
                  </NavLink>
                }
              />
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
