import type { FC } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import {
  AlertTriangle,
  FileCode,
  Gauge,
  CheckCircle2,
} from 'lucide-react';

export const LocalizationSection: FC = () => {
  const schemaFields = [
    {
      field: 'frameId',
      type: 'string',
      example: 'FRM-04821',
      description: 'Sequential camera frame identifier mapped to video stream buffer.',
    },
    {
      field: 'captureTimestamp',
      type: 'ISO-8601 UTC',
      example: '2026-10-30 14:22:18.120',
      description: 'Capture timestamp recorded at optical shutter release on ESP32-CAM.',
    },
    {
      field: 'inferenceTimestamp',
      type: 'ISO-8601 UTC',
      example: '2026-10-30 14:22:18.195',
      description: 'Evaluation timestamp recorded upon YOLO model inference completion on server.',
    },
    {
      field: 'eventArrivalTimestamp',
      type: 'ISO-8601 UTC',
      example: '2026-10-30 14:22:18.210',
      description: 'WebSocket telemetry arrival timestamp recorded on operator console.',
    },
    {
      field: 'defectClass',
      type: 'enum',
      example: 'deformation',
      description: 'Target class: deformation, misalignment, obstacle, or rupture.',
    },
    {
      field: 'confidenceScore',
      type: 'float [0.0 - 1.0]',
      example: '0.880',
      description: 'Statistical model probability output for bounding box prediction.',
    },
    {
      field: 'encoderTicks',
      type: 'uint32 (left/right)',
      example: '4,120 / 4,118',
      description: 'Rotary encoder interrupt pulses correlated at optical capture time.',
    },
    {
      field: 'estimatedDistance',
      type: 'float (meters)',
      example: '14.52 m',
      description: 'Linear odometry estimate from pipe entry point (subject to slip tolerances).',
    },
  ];

  return (
    <section className="py-16 lg:py-24 bg-industrial-50 border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                05 // Spatial Odometry
              </span>
              <Badge variant="outline" isMono>Defect Data Packet</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              Inspection Data Structure & Defect Localization
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              Every classified defect is synchronized with hardware odometry ticks to produce an indexed spatial record for engineering verification.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Data Schema: 8-Tuple Spatial Detection Packet
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Data Packet Table (7 cols on lg) */}
          <div className="lg:col-span-7 space-y-4">
            <Card variant="raised" className="border-industrial-300 overflow-hidden">
              <CardHeader className="bg-white pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileCode className="w-4 h-4 text-brand-orange" />
                    <CardTitle className="text-sm">Defect Detection Data Packet Schema</CardTitle>
                  </div>
                  <Badge variant="default" isMono className="text-[10px]">JSON Record</Badge>
                </div>
              </CardHeader>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-1/4">Field</TableHead>
                    <TableHead className="w-1/6">Type</TableHead>
                    <TableHead className="w-1/5">Example</TableHead>
                    <TableHead>Engineering Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {schemaFields.map((field) => (
                    <TableRow key={field.field}>
                      <TableCell className="font-mono text-xs font-bold text-industrial-900">
                        {field.field}
                      </TableCell>
                      <TableCell className="font-mono text-[11px] text-brand-orange">
                        {field.type}
                      </TableCell>
                      <TableCell className="font-mono text-[11px] text-industrial-700 bg-industrial-50">
                        {field.example}
                      </TableCell>
                      <TableCell className="text-xs text-industrial-600">
                        {field.description}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </div>

          {/* Right Column: Distance Estimation Mathematics & Wheel Slip Notice */}
          <div className="lg:col-span-5 space-y-6">
            <Card variant="raised" className="border-industrial-300">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-industrial-900" />
                  <CardTitle className="text-sm">Odometry Distance Formulation</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-0 text-xs text-industrial-700">
                <div className="p-3 bg-industrial-100 border border-industrial-300 rounded-sm font-mono text-center">
                  <span className="text-[11px] text-industrial-500 block mb-1">LINEAR DISTANCE FORMULA</span>
                  <span className="text-sm font-bold text-industrial-900">
                    D = [(Ticks_L + Ticks_R) / (2 x PPR)] x (pi x d_wheel)
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <span className="font-mono font-bold text-industrial-900 block">Variables:</span>
                  <ul className="space-y-1 font-mono text-[11px] text-industrial-600">
                    <li>• <strong>Ticks_L / Ticks_R</strong>: Accumulated interrupt count</li>
                    <li>• <strong>PPR</strong>: Pulses Per Revolution (Optical disc slots)</li>
                    <li>• <strong>d_wheel</strong>: Calibrated outer diameter of traction wheel</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Critical Wheel Slip & Physical Positioning Disclaimer */}
            <div className="p-5 bg-status-warning-bg border border-status-warning-border rounded-sm space-y-2">
              <div className="flex items-center gap-2 text-status-warning">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <h4 className="text-xs font-bold uppercase tracking-wide">
                  Physical Position Disclaimer & Wheel Slip
                </h4>
              </div>
              <p className="text-xs text-industrial-800 leading-relaxed">
                Reported defect locations are <strong>estimated distances</strong> derived from rotary encoder integration. Inside industrial PVC pipelines, moisture film, slime, slope, and silt accumulation induce physical wheel slip. Distance readings are subject to calibration tolerances and do not constitute absolute geodetic survey coordinates.
              </p>
              <div className="pt-2 border-t border-status-warning-border flex items-center gap-2 text-[11px] font-mono text-status-warning font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Operator verification required before excavation</span>
              </div>
            </div>

            {/* Hardware Synchronization Architecture Requirement */}
            <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm text-xs space-y-1.5 text-industrial-700">
              <span className="font-mono font-bold uppercase text-[10px] text-industrial-900 block">
                Future Integration Requirement: Dual-MCU Synchronization
              </span>
              <p className="text-[11px] leading-relaxed text-industrial-600">
                The ESP32-CAM (video) and ESP32-WROOM-32 (odometry) are independent microcontrollers. Frame-to-odometry association requires a synchronization protocol to link shutter capture events with tick counters. Spatial positioning must always correlate to capture time, never server-side YOLO inference completion time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
