import type { FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useDefects } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  CameraOff,
  Play,
  Pause,
  Square,
  Save,
  PlusCircle,
  ScanEye,
  Clock,
  AlertTriangle,
  Radio,
  Layers,
} from 'lucide-react';

export const InspectionPage: FC = () => {
  useDocumentTitle('Live Inspection');
  const { isDemoMode } = useAppMode();
  const { defects } = useDefects();

  const activeDetection = isDemoMode && defects.length > 0 ? defects[defects.length - 1] : null;

  return (
    <div className="space-y-6">
      {/* Informational Callout */}
      <div className="p-3.5 bg-industrial-100 border border-industrial-300 rounded-sm flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-brand-orange shrink-0 mt-0.5" />
        <div className="text-xs text-industrial-700 leading-relaxed">
          <span className="font-bold text-industrial-900 uppercase font-mono mr-1">
            Inspection Workspace Notice:
          </span>
          Hardware control and optical streaming will become available after backend integration. All mission controls remain safely locked in both prototype and demo modes.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Video Viewport & Mission Controls (8 cols on lg) */}
        <div className="lg:col-span-8 space-y-4">
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
                <StatusIndicator status="offline" label="Signal: Disconnected" size="sm" />
                <Badge variant="outline" isMono className="bg-industrial-800 text-white border-industrial-700 text-[10px]">
                  0.0 FPS
                </Badge>
              </div>
            </div>

            {/* Video Placeholder Area (Strictly No Fake Footage) */}
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

              <div className="p-4 bg-industrial-900 rounded-sm mb-3 border border-industrial-800 text-industrial-500">
                <CameraOff className="w-10 h-10" />
              </div>

              <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                Optical Feed Inactive
              </h3>
              <p className="mt-1 text-xs text-industrial-400 max-w-sm font-mono">
                No active MJPEG video stream detected at local camera endpoint. Awaiting ESP32-CAM wireless link establishment.
              </p>

              <div className="mt-4 flex items-center gap-3 font-mono text-[11px] text-industrial-500">
                <span>Resolution: 640 x 480 (VGA)</span>
                <span>•</span>
                <span>Port: 8000 /stream</span>
              </div>
            </div>

            {/* Operational Inspection Controls (Genuinely Disabled in All Modes) */}
            <div className="p-4 bg-white flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  disabled
                  leftIcon={<Play className="w-3.5 h-3.5" />}
                  title="Hardware control will become available after backend integration"
                >
                  Start Run
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  disabled
                  leftIcon={<Pause className="w-3.5 h-3.5" />}
                  title="Hardware control will become available after backend integration"
                >
                  Pause
                </Button>

                <Button
                  variant="danger"
                  size="sm"
                  disabled
                  leftIcon={<Square className="w-3.5 h-3.5" />}
                  title="Hardware control will become available after backend integration"
                >
                  Stop
                </Button>

                <div className="h-4 w-px bg-industrial-200 hidden sm:block mx-1" />

                <Button
                  variant="outline"
                  size="sm"
                  disabled
                  leftIcon={<PlusCircle className="w-3.5 h-3.5" />}
                  title="Hardware control will become available after backend integration"
                >
                  New Mission
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  disabled
                  leftIcon={<Save className="w-3.5 h-3.5" />}
                  title="Hardware control will become available after backend integration"
                >
                  Save Log
                </Button>
              </div>

              <div className="text-[11px] font-mono text-industrial-500">
                Mode: <span className="text-industrial-900 font-bold">{isDemoMode ? 'DEMO' : 'Idle'}</span>
              </div>
            </div>
          </Card>

          {/* Inspection Mission Timeline Card */}
          <Card variant="default" className="border-industrial-200">
            <CardHeader className="p-4 pb-2 border-b border-industrial-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs uppercase font-mono tracking-wider">
                  Mission Traversal Timeline
                </CardTitle>
                <CardDescription className="text-xs">
                  Linear distance progression and chronological defect bookmark markers
                </CardDescription>
              </div>
              <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                {isDemoMode ? `${defects.length} Demo Events` : '0 Events'}
              </Badge>
            </CardHeader>

            <CardContent className="p-6">
              {isDemoMode && defects.length > 0 ? (
                <div className="space-y-4 font-mono">
                  <div className="relative border-l-2 border-industrial-300 ml-4 pl-6 space-y-6">
                    {defects.map((defect) => (
                      <div key={defect.id} className="relative">
                        <div className="absolute -left-[31px] top-0 w-3.5 h-3.5 rounded-full bg-brand-orange border-2 border-white shadow-sm" />
                        <div className="p-3 bg-industrial-50 border border-industrial-200 rounded-sm">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-industrial-900">{defect.id} | {defect.defectClass.toUpperCase()}</span>
                            <Badge variant="outline" isMono className="text-[10px]">
                              {defect.estimatedDistanceMeters?.toFixed(2)} m
                            </Badge>
                          </div>
                          <div className="text-[11px] text-industrial-500 mt-1 flex flex-wrap gap-x-4">
                            <span>Capture Time: {defect.captureTimestamp}</span>
                            <span>Frame: {defect.frameId}</span>
                            <span>Confidence: {defect.confidence ? `${(defect.confidence * 100).toFixed(0)}%` : '--'}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-6 bg-industrial-50 border border-dashed border-industrial-300 rounded-sm text-center">
                  <Clock className="w-6 h-6 text-industrial-400 mx-auto mb-2" />
                  <h4 className="text-xs font-mono font-bold text-industrial-800 uppercase">
                    Timeline Dormant
                  </h4>
                  <p className="mt-1 text-xs text-industrial-500 font-mono">
                    Traversal distance markers and classified anomaly events will populate this timeline sequentially during an inspection run.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: AI Defect Detections Panel (4 cols on lg) */}
        <div className="lg:col-span-4 space-y-4">
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="p-4 pb-3 border-b border-industrial-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ScanEye className="w-4 h-4 text-brand-orange" />
                  <CardTitle className="text-sm">Real-Time Detections</CardTitle>
                </div>
                <Badge variant={isDemoMode ? 'brand' : 'outline'} isMono className="text-[10px]">
                  {isDemoMode ? 'DEMO DATA' : 'YOLO v8 Head'}
                </Badge>
              </div>
              <CardDescription className="text-xs mt-1">
                Anomalies classified by server-side computer vision
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 space-y-4">
              <div className="p-4 bg-industrial-50 border border-industrial-200 rounded-sm space-y-3">
                <div className="flex items-center justify-between border-b border-industrial-200 pb-2">
                  <span className="text-xs font-mono font-bold uppercase text-industrial-700">
                    Detection Telemetry Fields
                  </span>
                  <StatusIndicator
                    status={isDemoMode ? 'healthy' : 'offline'}
                    label={isDemoMode ? 'Demo Active' : 'Dormant'}
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
                      {activeDetection?.confidence ? `${(activeDetection.confidence * 100).toFixed(1)}%` : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Frame Identifier:</span>
                    <span className="text-industrial-700">{activeDetection?.frameId || 'FRM-00000'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Capture Time:</span>
                    <span className="text-industrial-700">{activeDetection?.captureTimestamp || '--:--:--.---'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-industrial-100">
                    <span className="text-industrial-500">Inference Time:</span>
                    <span className="text-industrial-700">{activeDetection?.inferenceTimestamp || '--:--:--.---'}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-industrial-500">Estimated Distance:</span>
                    <span className="font-bold text-industrial-900">
                      {activeDetection?.estimatedDistanceMeters !== null && activeDetection?.estimatedDistanceMeters !== undefined
                        ? `${activeDetection.estimatedDistanceMeters.toFixed(2)} m`
                        : '0.00 m'}
                    </span>
                  </div>
                </div>
              </div>

              {!isDemoMode && (
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
    </div>
  );
};

export default InspectionPage;
