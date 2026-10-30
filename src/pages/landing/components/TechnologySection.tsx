import type { FC } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  Code,
  Server,
  Cpu,
  Database,
  Radio,
} from 'lucide-react';

export const TechnologySection: FC = () => {
  const stackLayers = [
    {
      id: 'frontend',
      title: 'Frontend Web Console',
      status: 'Implemented (Stages 1-2)',
      badgeVariant: 'healthy' as const,
      icon: Code,
      items: [
        { name: 'React 18', role: 'Component hierarchy & view reconciliation' },
        { name: 'TypeScript 5', role: 'Strict type safety across domain interfaces' },
        { name: 'Vite 6', role: 'Fast HMR dev server & optimized rollup production bundling' },
        { name: 'Tailwind CSS 3.4', role: 'Industrial token-based responsive styling' },
        { name: 'React Router 6', role: 'Client-side nested routing and view state' },
        { name: 'Lucide React', role: 'Consistent engineering iconography' },
      ],
    },
    {
      id: 'backend',
      title: 'Processing Backend Server',
      status: 'Planned Architecture (Stage 5)',
      badgeVariant: 'warning' as const,
      icon: Server,
      items: [
        { name: 'Python 3.11', role: 'Host processing runtime environment' },
        { name: 'FastAPI', role: 'Asynchronous REST APIs & WebSocket broker' },
        { name: 'OpenCV', role: 'MJPEG stream ingestion, frame slicing & buffering' },
        { name: 'WebSockets', role: 'Sub-millisecond telemetry & frame streaming' },
        { name: 'NumPy', role: 'Numerical odometry calculation and vector math' },
      ],
    },
    {
      id: 'ai',
      title: 'Artificial Intelligence & Vision',
      status: 'Model Integration Target',
      badgeVariant: 'default' as const,
      icon: Cpu,
      items: [
        { name: 'PyTorch', role: 'Deep learning neural network execution backend' },
        { name: 'Ultralytics YOLO', role: 'Convolutional object detection & bounding box head' },
        { name: 'Custom Conduit Dataset', role: 'Deformation, Misalignment, Obstacle, Rupture' },
        { name: 'Confidence Filter', role: 'Operator thresholding and false-positive filtering' },
      ],
    },
    {
      id: 'embedded',
      title: 'Embedded Hardware Stack',
      status: 'Hardware Target Specification',
      badgeVariant: 'default' as const,
      icon: Radio,
      items: [
        { name: 'AI Thinker ESP32-CAM', role: 'OV2640 2MP sensor & local video streaming' },
        { name: 'ESP32-WROOM-32', role: 'Dual-core MCU for motor PWM & odometry ticks' },
        { name: 'MPU6050', role: '6-axis accelerometer & gyroscope for incline angle' },
        { name: 'Dual Optical Encoders', role: 'Quadrature wheel pulses for distance odometry' },
        { name: 'Dual H-Bridge Driver', role: 'DC motor current control and directional drive' },
      ],
    },
    {
      id: 'storage',
      title: 'Persistence & Archiving',
      status: 'Schema Specified',
      badgeVariant: 'outline' as const,
      icon: Database,
      items: [
        { name: 'SQLite', role: 'Local embedded relational database for mission records' },
        { name: 'PostgreSQL (Future)', role: 'Multi-operator centralized municipal pipeline database' },
        { name: 'Local File Archive', role: 'Indexed raw JPEG frames and detection overlays' },
        { name: 'Structured JSON', role: 'Standardized telemetry stream and defect export files' },
      ],
    },
  ];

  return (
    <section id="technology" className="py-16 lg:py-24 bg-white border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                06 // Technical Specifications
              </span>
              <Badge variant="outline" isMono>5-Layer Technology Stack</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              Technology Stack & System Layers
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              Clear delineation between currently active frontend components and planned embedded and backend modules.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Status: Frontend Operational / Hardware Target Defined
          </div>
        </div>

        {/* 5 Stack Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stackLayers.map((layer) => {
            const Icon = layer.icon;
            return (
              <Card key={layer.id} variant="raised" className="border-industrial-300 flex flex-col justify-between">
                <div>
                  <CardHeader className="pb-3 border-b border-industrial-200">
                    <div className="flex items-center justify-between">
                      <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm">
                        <Icon className="w-4 h-4" />
                      </div>
                      <Badge variant={layer.badgeVariant} isMono className="text-[10px]">
                        {layer.status}
                      </Badge>
                    </div>
                    <CardTitle className="text-base mt-2">{layer.title}</CardTitle>
                  </CardHeader>

                  <CardContent className="pt-4">
                    <ul className="space-y-2.5">
                      {layer.items.map((tech) => (
                        <li key={tech.name} className="text-xs font-mono border-b border-industrial-100 pb-2 last:border-b-0 last:pb-0">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-industrial-900">{tech.name}</span>
                          </div>
                          <span className="text-[11px] text-industrial-500 block mt-0.5">
                            {tech.role}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </div>

                <div className="p-3 bg-industrial-50 border-t border-industrial-200 text-[11px] font-mono text-industrial-500 flex items-center justify-between">
                  <span>Layer: {layer.id.toUpperCase()}</span>
                  <span>v0.1 Arch</span>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
