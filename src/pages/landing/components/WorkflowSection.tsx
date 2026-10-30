import type { FC } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  LogIn,
  Camera,
  Wifi,
  Cpu,
  Ruler,
  Database,
  AlertCircle,
} from 'lucide-react';

export const WorkflowSection: FC = () => {
  const steps = [
    {
      step: '01',
      title: 'Vehicle Enters Pipeline',
      subsystem: 'Crawler Chassis Insertion',
      description:
        'The 4-wheel inspection crawler is positioned at an access chamber or pipeline cleanout. Motors engage at controlled crawl velocity, aligning the chassis along the pipe invert.',
      icon: LogIn,
      domain: 'Mechanical Domain',
    },
    {
      step: '02',
      title: 'Internal Footage Capture',
      subsystem: 'AI Thinker ESP32-CAM',
      description:
        'The forward-mounted OV2640 sensor continuously captures pipeline interior frames illuminated by the high-output LED array. Frames are buffered in microcontroller PSRAM.',
      icon: Camera,
      domain: 'Capture Domain (t0)',
    },
    {
      step: '03',
      title: 'Local Server Transmission',
      subsystem: '2.4 GHz Local Wi-Fi Stream',
      description:
        'Video frames and motor telemetry are streamed via local wireless network to an edge processing workstation. No cloud upload is required for the real-time inspection loop.',
      icon: Wifi,
      domain: 'Transport Domain (t1)',
    },
    {
      step: '04',
      title: 'YOLO Model Inference',
      subsystem: 'Processing Server (Python / PyTorch)',
      description:
        'The server-side YOLO model processes incoming frames. When anomalies (cracks, deformation, blockage, misalignment) are detected, bounding boxes and confidence scores are generated.',
      icon: Cpu,
      domain: 'Inference Domain (t2)',
    },
    {
      step: '05',
      title: 'Encoder Distance Estimation',
      subsystem: 'Dual Optical Odometry Fusion',
      description:
        'Simultaneous telemetry from left and right wheel encoders is correlated with the detection timestamp, associating each defect with its estimated distance from the entry point.',
      icon: Ruler,
      domain: 'Spatial Domain',
    },
    {
      step: '06',
      title: 'Inspection Record Storage',
      subsystem: 'Database & Operator Console',
      description:
        'Detection metadata, bounding box coordinates, encoder distance markers, and high-resolution frame captures are archived in the local inspection database for operator review.',
      icon: Database,
      domain: 'Persistence Domain',
    },
  ];

  return (
    <section id="process" className="py-16 lg:py-24 bg-white border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                02 // Inspection Process
              </span>
              <Badge variant="outline" isMono>6 Sequential Stages</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              End-to-End Inspection & Processing Workflow
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              Step-by-step progression from robotic conduit entry to synchronized defect localization and data persistence.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Execution Flow: Synchronous Ingestion / Asynchronous Inference
          </div>
        </div>

        {/* Workflow Timeline Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative">
          {steps.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.step} variant="default" className="relative hover:border-industrial-400 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-2xl font-black text-industrial-300">
                      {item.step}
                    </span>
                    <Badge variant="outline" isMono className="text-[10px]">
                      {item.domain}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="p-1.5 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <CardTitle className="text-sm">{item.title}</CardTitle>
                  </div>
                  <span className="font-mono text-[11px] text-brand-orange block font-medium">
                    {item.subsystem}
                  </span>
                </CardHeader>
                <CardContent className="pt-0 text-xs text-industrial-600 leading-relaxed">
                  {item.description}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Technical Callout Card: Decoupled Architecture Distinction */}
        <div className="mt-10 p-5 bg-industrial-100 border border-industrial-300 rounded-sm">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0 mt-0.5">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-industrial-900 uppercase tracking-wide">
                Engineering Architecture Distinction: Capture vs. Inference Timing
              </h3>
              <p className="text-xs text-industrial-700 leading-relaxed">
                Optical frame acquisition occurs in real time on the <strong>AI Thinker ESP32-CAM</strong> micro-module at capture time. In contrast, heavy computer vision inference using <strong>Ultralytics YOLO</strong> executes asynchronously on an external edge workstation / local server. The ESP32 microcontrollers are neither designed nor utilized for convolutional neural network inference.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

