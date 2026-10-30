import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useInspection, useSystemStatus, useDefects } from '@/app/providers/AppContext';
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
  const { defects } = useDefects();
  const { systemStatus, backendOnline } = useSystemStatus();

  const isBackendActive = isDemoMode || backendOnline || systemStatus.backend === 'connected';
  const isHardwareActive = isDemoMode || systemStatus.hardware === 'connected';
  const isCameraActive = !isDemoMode && systemStatus.camera === 'connected';
  const isAiActive = isDemoMode || systemStatus.aiProcessing === 'connected';

  const subsystemStates = [
    {
      name: 'Hardware Controller',
      device: 'ESP32-WROOM-32',
      status: (isHardwareActive ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isHardwareActive
        ? isDemoMode ? 'Simulated Active' : 'Controller Linked'
        : 'Not connected',
      note: isHardwareActive
        ? 'Dual encoder odometry & MPU6050 link active'
        : 'Awaiting local Wi-Fi / Serial link',
      icon: Cpu,
    },
    {
      name: 'Optical Camera',
      device: 'AI Thinker ESP32-CAM',
      status: (isCameraActive ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isCameraActive ? 'Stream Online' : 'Not connected',
      note: isCameraActive
        ? 'MJPEG video ingestion active at /stream'
        : 'Awaiting ESP32-CAM link establishment',
      icon: Camera,
    },
    {
      name: 'AI Inference Server',
      device: 'Ultralytics YOLO (PyTorch)',
      status: (isAiActive ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isAiActive
        ? isDemoMode ? 'Model Ready (Demo)' : 'Inference Active'
        : 'Not connected',
      note: isAiActive
        ? 'Evaluated 4 dataset anomaly classes'
        : 'Edge vision pipeline dormant',
      icon: Layers,
    },
    {
      name: 'Processing Backend',
      device: 'Python FastAPI Engine',
      status: (isBackendActive ? 'healthy' : 'offline') as 'healthy' | 'offline',
      label: isBackendActive
        ? isDemoMode ? 'Simulated Broker' : 'FastAPI Connected'
        : 'Not connected',
      note: isBackendActive
        ? 'REST & WebSocket broker active'
        : 'REST & WebSocket broker unlinked',
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
      title: 'Defect Registry',
      description: `Review detected anomalies (${defects.length} cataloged), bounding boxes, and verify states.`,
      path: ROUTES.DASHBOARD.DEFECTS,
      icon: AlertOctagon,
      badge: `${defects.length} logged`,
    },
    {
      title: 'Mission History',
      description: `Access chronological run records (${inspections.length} recorded), distance metrics, and exports.`,
      path: ROUTES.DASHBOARD.HISTORY,
      icon: History,
      badge: `${inspections.length} runs`,
    },
    {
      title: 'Inspection Reports',
      description: 'Generate compliance summaries, ASTM ratings, and structured JSON/PDF outputs.',
      path: ROUTES.DASHBOARD.REPORTS,
      icon: FileText,
      badge: 'Audit',
    },
    {
      title: 'Odometry & Telemetry',
      description: 'Inspect pulse counts, crawl speeds, tilt angles, and battery health in real-time.',
      path: ROUTES.DASHBOARD.TELEMETRY,
      icon: Activity,
      badge: 'Sensors',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Prototype Workspace Guidance Callout */}
      <div className="p-3.5 bg-industrial-100 border border-industrial-300 rounded-sm flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-brand-orange shrink-0 mt-0.5" />
        <div className="text-xs text-industrial-700 leading-relaxed">
          <span className="font-bold text-industrial-900 uppercase font-mono mr-1">
            System Operational Status:
          </span>
          {isDemoMode
            ? 'Viewing simulated dataset preview. Exit Demo Mode to monitor genuine pipeline hardware telemetry.'
            : isBackendActive
            ? 'FastAPI processing backend connected to active SQLite database. Ready for pipeline mission tracking.'
            : 'Processing backend unlinked. Launch FastAPI server on 127.0.0.1:8000 to ingest live telemetry and store inspection records.'}
        </div>
      </div>

      {/* Subsystem Connection Matrix */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
            Subsystem Link Status Matrix
          </h2>
          <span className="text-[11px] font-mono text-industrial-500">
            {isDemoMode ? 'SIMULATED DATASET' : 'VERIFIED TELEMETRY STATE'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {subsystemStates.map((subsystem) => {
            const Icon = subsystem.icon;
            return (
              <Card key={subsystem.name} variant="default" className="border-industrial-300">
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2 bg-industrial-100 rounded-sm text-industrial-800">
                      <Icon className="w-4 h-4" />
                    </div>
                    <StatusIndicator
                      status={subsystem.status}
                      size="sm"
                      label={subsystem.label}
                    />
                  </div>

                  <div>
                    <h3 className="font-bold text-xs text-industrial-950 tracking-tight">
                      {subsystem.name}
                    </h3>
                    <p className="font-mono text-[11px] text-industrial-500">{subsystem.device}</p>
                  </div>

                  <div className="pt-2 border-t border-industrial-100 text-[11px] font-mono text-industrial-600">
                    {subsystem.note}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Primary Navigation Bento Grid */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono mb-3">
          Mission Workspaces
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActionCards.map((card) => {
            const Icon = card.icon;
            return (
              <NavLink
                key={card.path}
                to={card.path}
                className="group block focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-orange"
              >
                <Card
                  variant="raised"
                  className="h-full border-industrial-300 transition-all hover:border-industrial-900 flex flex-col justify-between"
                >
                  <CardHeader className="p-5 pb-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="p-2.5 bg-industrial-100 text-industrial-900 group-hover:bg-brand-orange group-hover:text-white transition-colors rounded-sm">
                        <Icon className="w-5 h-5" />
                      </div>
                      <Badge variant="outline" isMono className="text-[10px]">
                        {card.badge}
                      </Badge>
                    </div>
                    <CardTitle className="text-sm group-hover:text-brand-orange transition-colors">
                      {card.title}
                    </CardTitle>
                    <CardDescription className="text-xs mt-1 leading-relaxed">
                      {card.description}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="p-5 pt-0">
                    <div className="pt-3 border-t border-industrial-100 flex items-center justify-between text-xs font-mono text-industrial-600 group-hover:text-industrial-950">
                      <span>Access Workspace</span>
                      <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                    </div>
                  </CardContent>
                </Card>
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* Diagnostic & Telemetry Overview Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Core Capabilities Card */}
        <div className="lg:col-span-7 space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-industrial-800 font-mono">
            Pipeline Crawl Architecture
          </h2>

          <Card variant="default" className="border-industrial-200 p-5 space-y-4">
            <p className="text-xs text-industrial-700 leading-relaxed">
              PipeBot operates inside PVC and utility conduits using low-profile chassis crawler mechanics. Continuous odometry from dual magnetic rotary encoders is paired with MPU6050 inertial tilt measurements to log spatial defect coordinates without requiring internal GPS.
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2 font-mono text-xs">
              <div className="p-3 bg-industrial-100 rounded-sm">
                <span className="text-[10px] text-industrial-500 uppercase block">Wheel Track Baseline</span>
                <span className="font-bold text-industrial-900">120 mm Gauge</span>
              </div>
              <div className="p-3 bg-industrial-100 rounded-sm">
                <span className="text-[10px] text-industrial-500 uppercase block">Target Conduits</span>
                <span className="font-bold text-industrial-900">150 - 300 mm ID</span>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-industrial-100">
              <span className="text-[11px] font-mono text-industrial-500 block uppercase font-bold">
                Target Anomaly Classes (Roboflow v7 YOLO Model):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {['Deformation', 'Misalignment', 'Obstacle', 'Rupture'].map((cls, idx) => (
                  <Badge key={cls} variant="outline" isMono className="text-[11px]">
                    <span className="text-brand-orange font-bold mr-1">#{idx}</span> {cls}
                  </Badge>
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Inspection Runs */}
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
                      {isDemoMode ? 'DEMO RECORD' : 'MISSION RECORD'}
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
                    <span className="font-bold text-brand-orange">
                      {inspections[0]?.totalDistanceMeters != null
                        ? `${inspections[0].totalDistanceMeters.toFixed(2)} m`
                        : '--'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Defects Logged:</span>
                    <span className="font-bold text-status-critical">{inspections[0]?.defectCount ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-500">Started At:</span>
                    <span className="text-[11px] text-industrial-500">
                      {inspections[0]?.startedAt ? new Date(inspections[0].startedAt).toLocaleString() : '--'}
                    </span>
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
