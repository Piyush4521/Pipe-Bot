import { useState, type FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useDefects, useTelemetry, useInspection } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { EmptyState } from '@/components/ui/EmptyState';
import { PipeTimeline } from '@/components/inspection/PipeTimeline';
import { CameraStreamControls } from '@/components/inspection/CameraStreamControls';
import { NewInspectionModal } from '@/components/inspection/NewInspectionModal';
import {
  CameraOff,
  Play,
  Pause,
  Square,
  PlusCircle,
  ScanEye,
  AlertTriangle,
  Radio,
  Layers,
} from 'lucide-react';

export const InspectionPage: FC = () => {
  useDocumentTitle('Live Inspection');
  const { isDemoMode } = useAppMode();
  const { defects } = useDefects();
  const { encoderTelemetry } = useTelemetry();
  const { inspections, refreshData } = useInspection();

  const [isModalOpen, setIsModalOpen] = useState(false);

  const activeDetection = defects.length > 0 ? defects[defects.length - 1] : null;
  const currentDistance = encoderTelemetry.estimatedDistanceMeters;

  return (
    <div className="space-y-6">
      {/* Informational Callout */}
      <div className="p-3.5 bg-industrial-100 border border-industrial-300 rounded-sm flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-brand-orange shrink-0 mt-0.5" />
        <div className="text-xs text-industrial-700 leading-relaxed">
          <span className="font-bold text-industrial-900 uppercase font-mono mr-1">
            Inspection Workspace:
          </span>
          {isDemoMode
            ? 'Viewing simulated optical detection preview. Exit Demo Mode to monitor live camera ingestion and hardware telemetry.'
            : 'FastAPI vision and ingestion backend ready. Use Camera Controls below to connect ESP32-CAM stream or upload sample test frames.'}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Video Viewport & Controls (8 cols on lg) */}
        <div className="lg:col-span-8 space-y-5">
          {/* Main Video Viewport Card */}
          <Card variant="raised" className="border-industrial-300 overflow-hidden">
            {/* Viewport Status Header */}
            <div className="px-4 py-2.5 bg-industrial-900 text-white flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 text-industrial-400" />
                <span className="font-bold uppercase tracking-wider">
                  Source: ESP32-CAM (OV2640 Optical Feed)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <StatusIndicator
                  status={isDemoMode ? 'healthy' : 'offline'}
                  label={isDemoMode ? 'Feed: Simulated' : 'Feed: Awaiting Stream'}
                  size="sm"
                />
                <Badge variant="outline" isMono className="bg-industrial-800 text-white border-industrial-700 text-[10px]">
                  {isDemoMode ? '15.0 FPS' : '0.0 FPS'}
                </Badge>
              </div>
            </div>

            {/* Video Viewport Area */}
            <div className="relative aspect-video bg-industrial-950 flex flex-col items-center justify-center p-8 text-center select-none border-b border-industrial-900">
              {/* Subtle Viewfinder Reticle Corners */}
              <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-industrial-700 pointer-events-none" />
              <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-industrial-700 pointer-events-none" />
              <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-industrial-700 pointer-events-none" />
              <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-industrial-700 pointer-events-none" />

              {/* Center Screen Crosshair */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                <div className="w-16 h-px bg-industrial-400" />
                <div className="h-16 w-px bg-industrial-400 -ml-8" />
              </div>

              {activeDetection?.snapshotUrl ? (
                <img
                  src={activeDetection.snapshotUrl}
                  alt="Optical frame"
                  className="max-h-full max-w-full object-contain"
                />
              ) : (
                <>
                  <div className="p-4 bg-industrial-900 rounded-sm mb-3 border border-industrial-800 text-industrial-500">
                    <CameraOff className="w-10 h-10" />
                  </div>

                  <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                    {isDemoMode ? 'Simulated Optical View' : 'Optical Feed Inactive'}
                  </h3>
                  <p className="mt-1 text-xs text-industrial-400 max-w-sm font-mono">
                    {isDemoMode
                      ? 'Simulated conduit feed displaying target defect classes.'
                      : 'No active MJPEG stream connected. Connect stream via Camera Controls or upload frame for inference.'}
                  </p>
                </>
              )}

              <div className="mt-4 flex items-center gap-3 font-mono text-[11px] text-industrial-500">
                <span>Resolution: 640 x 480 (VGA)</span>
                <span>•</span>
                <span>Port: 8000 /api/v1/camera/stream</span>
              </div>
            </div>

            {/* Operational Inspection Controls */}
            <div className="p-4 bg-white flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setIsModalOpen(true)}
                  leftIcon={<PlusCircle className="w-3.5 h-3.5" />}
                >
                  New Mission
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  disabled
                  leftIcon={<Play className="w-3.5 h-3.5" />}
                  title="Actuation interlocked until safety switch confirmed"
                >
                  Start Run
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  disabled
                  leftIcon={<Pause className="w-3.5 h-3.5" />}
                  title="Actuation interlocked until safety switch confirmed"
                >
                  Pause
                </Button>

                <Button
                  variant="danger"
                  size="sm"
                  disabled
                  leftIcon={<Square className="w-3.5 h-3.5" />}
                  title="Actuation interlocked until safety switch confirmed"
                >
                  Stop
                </Button>
              </div>

              <div className="text-[11px] font-mono text-industrial-500">
                Status: <span className="text-industrial-900 font-bold">{isDemoMode ? 'DEMO' : 'ACTIVE'}</span>
              </div>
            </div>
          </Card>

          {/* Longitudinal Conduit Timeline */}
          <PipeTimeline
            defects={defects}
            currentDistanceMeters={currentDistance}
            totalLengthMeters={inspections[0]?.totalDistanceMeters ?? 20}
          />

          {/* Camera Ingestion Controls */}
          <CameraStreamControls onFrameProcessed={() => refreshData()} />
        </div>

        {/* Right Column: AI Defect Detections Panel (4 cols on lg) */}
        <div className="lg:col-span-4 space-y-4">
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="p-4 pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ScanEye className="w-4 h-4 text-brand-orange" />
                  <CardTitle className="text-sm">Latest Anomaly Detection</CardTitle>
                </div>
                <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                  {isDemoMode ? 'DEMO DATA' : 'YOLO v8'}
                </Badge>
              </div>
              <CardDescription className="text-xs mt-1">
                Evaluated by server-side computer vision
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 space-y-4">
              <div className="p-4 bg-industrial-50 border border-industrial-200 rounded-sm space-y-3">
                <div className="flex items-center justify-between border-b border-industrial-200 pb-2">
                  <span className="text-xs font-mono font-bold uppercase text-industrial-700">
                    Detection Telemetry Fields
                  </span>
                  <StatusIndicator
                    status={activeDetection ? 'healthy' : 'offline'}
                    label={activeDetection ? 'Detection Logged' : 'Dormant'}
                    size="sm"
                  />
                </div>

                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Defect Class:</span>
                    <span className="font-bold text-industrial-900">
                      {activeDetection ? activeDetection.defectClass.toUpperCase() : 'None detected'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Confidence Score:</span>
                    <span className="font-bold text-brand-orange">
                      {activeDetection?.confidence != null
                        ? `${(activeDetection.confidence * 100).toFixed(1)}%`
                        : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Frame Identifier:</span>
                    <span className="text-industrial-700">{activeDetection?.frameId || 'FRM-00000'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Capture Time:</span>
                    <span className="text-industrial-700">
                      {activeDetection?.captureTimestamp
                        ? new Date(activeDetection.captureTimestamp).toLocaleTimeString()
                        : '--:--:--.---'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Review State:</span>
                    <span className="font-bold uppercase text-industrial-900">
                      {activeDetection?.reviewStatus || 'UNREVIEWED'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-industrial-500">Estimated Distance:</span>
                    <span className="font-bold text-industrial-900">
                      {activeDetection?.estimatedDistanceMeters != null
                        ? `${activeDetection.estimatedDistanceMeters.toFixed(2)} m`
                        : '0.00 m'}
                    </span>
                  </div>
                </div>
              </div>

              {!activeDetection && (
                <EmptyState
                  icon={<Layers className="w-6 h-6 text-industrial-400" />}
                  title="No Defect Detections"
                  description="Live bounding boxes, confidence ratings, and spatial markers will log here in real time as the pipeline crawler progresses."
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* New Mission Modal */}
      <NewInspectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => refreshData()}
      />
    </div>
  );
};

export default InspectionPage;
