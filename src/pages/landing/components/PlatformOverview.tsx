import type { FC } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  Sliders,
  Camera,
  ScanEye,
  Ruler,
  FileSpreadsheet,
  CheckCircle2,
} from 'lucide-react';

export const PlatformOverview: FC = () => {
  return (
    <section id="overview" className="py-16 lg:py-24 bg-industrial-50 border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                01 // System Overview
              </span>
              <Badge variant="outline" isMono>5 Modular Subsystems</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              Core Subsystems of the PipeBot Platform
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              Designed as an end-to-end pipeline assessment pipeline, separating low-level motion control from high-bandwidth video capture and server-side machine learning inference.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Architecture: Dual-Microcontroller Topology
          </div>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Robotic Mobility */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="p-2.5 bg-industrial-900 text-brand-orange rounded-sm">
                  <Sliders className="w-5 h-5" />
                </div>
                <Badge variant="default" isMono>Subsystem 01</Badge>
              </div>
              <CardTitle className="text-base mt-2">Robotic Mobility Subsystem</CardTitle>
              <CardDescription>Four-wheel independent crawling inside circular conduits</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs text-industrial-700">
              <p className="leading-relaxed">
                A dedicated four-wheel inspection vehicle designed to navigate horizontal PVC pipes. Propulsion is controlled by an ESP32-WROOM-32 through dual H-Bridge motor drivers.
              </p>
              <ul className="space-y-1.5 pt-2 border-t border-industrial-100 font-mono">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Four high-traction DC geared motors</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>ESP32-WROOM-32 motor & sensor controller</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Bidirectional drive & crawl speed regulation</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Card 2: Internal Imaging */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="p-2.5 bg-industrial-900 text-brand-orange rounded-sm">
                  <Camera className="w-5 h-5" />
                </div>
                <Badge variant="default" isMono>Subsystem 02</Badge>
              </div>
              <CardTitle className="text-base mt-2">Internal Pipeline Imaging</CardTitle>
              <CardDescription>Forward-facing camera payload with localized illumination</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs text-industrial-700">
              <p className="leading-relaxed">
                Optical capture is handled by an AI Thinker ESP32-CAM module carrying an OV2640 2-megapixel image sensor. A high-intensity LED array illuminates the dark pipeline interior.
              </p>
              <ul className="space-y-1.5 pt-2 border-t border-industrial-100 font-mono">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>AI Thinker ESP32-CAM (OV2640 sensor)</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Dedicated Wi-Fi MJPEG video streaming</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>High-output LED forward ring illumination</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Card 3: AI Defect Detection */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="p-2.5 bg-industrial-900 text-brand-orange rounded-sm">
                  <ScanEye className="w-5 h-5" />
                </div>
                <Badge variant="brand" isMono>Subsystem 03</Badge>
              </div>
              <CardTitle className="text-base mt-2">AI Defect Detection</CardTitle>
              <CardDescription>YOLO-based computer vision executed on processing server</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs text-industrial-700">
              <p className="leading-relaxed">
                Incoming frames are ingested by a server-side Python OpenCV and Ultralytics YOLO pipeline. The model classifies structural anomalies and computes bounding boxes with confidence scores.
              </p>
              <ul className="space-y-1.5 pt-2 border-t border-industrial-100 font-mono">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Ultralytics YOLO detection architecture</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Confidence scoring & anomaly grading</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Zero micro-controller compute bottleneck</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Card 4: Defect Localization */}
          <Card variant="raised" className="border-industrial-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="p-2.5 bg-industrial-900 text-brand-orange rounded-sm">
                  <Ruler className="w-5 h-5" />
                </div>
                <Badge variant="default" isMono>Subsystem 04</Badge>
              </div>
              <CardTitle className="text-base mt-2">Defect Spatial Localization</CardTitle>
              <CardDescription>Dual wheel encoder odometry correlated with video frames</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs text-industrial-700">
              <p className="leading-relaxed">
                Left and right optical wheel encoders record rotation pulses to calculate estimated linear traversal. Each detected defect frame is tagged with its spatial distance marker.
              </p>
              <ul className="space-y-1.5 pt-2 border-t border-industrial-100 font-mono">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Dual optical encoder pulse tracking</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Linear distance calculation along pipe axis</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-status-healthy shrink-0" />
                  <span>Defect-to-odometry frame correlation</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Card 5: Inspection Records & Reporting (Spans 2 cols on lg) */}
          <Card variant="raised" className="md:col-span-2 lg:col-span-2 border-industrial-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="p-2.5 bg-industrial-900 text-brand-orange rounded-sm">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <Badge variant="default" isMono>Subsystem 05</Badge>
              </div>
              <CardTitle className="text-base mt-2">Inspection Records & Reporting Management</CardTitle>
              <CardDescription>Mission cataloguing, frame preservation, and structured engineering summaries</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs text-industrial-700">
              <p className="leading-relaxed">
                Centralized database management stores every inspection run, defect position, classification confidence, and raw visual frame. Engineers can review historical runs and generate automated inspection summaries.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-industrial-100 font-mono text-[11px]">
                <div className="p-2.5 bg-white border border-industrial-200 rounded-sm">
                  <span className="font-bold text-industrial-900 block">Mission Archives</span>
                  <span className="text-industrial-500">Pipe ID, run date, operator logs</span>
                </div>
                <div className="p-2.5 bg-white border border-industrial-200 rounded-sm">
                  <span className="font-bold text-industrial-900 block">Defect Registry</span>
                  <span className="text-industrial-500">Coordinates, class, bounding boxes</span>
                </div>
                <div className="p-2.5 bg-white border border-industrial-200 rounded-sm">
                  <span className="font-bold text-industrial-900 block">Report Generation</span>
                  <span className="text-industrial-500">Summary export for maintenance sign-off</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

