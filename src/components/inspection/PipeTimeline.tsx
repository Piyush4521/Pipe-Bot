import { type FC, useState } from 'react';
import type { DefectDetection } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Ruler, AlertCircle } from 'lucide-react';

interface PipeTimelineProps {
  defects: DefectDetection[];
  currentDistanceMeters?: number | null;
  totalLengthMeters?: number;
  onSelectDefect?: (defect: DefectDetection) => void;
}

export const PipeTimeline: FC<PipeTimelineProps> = ({
  defects,
  currentDistanceMeters = null,
  totalLengthMeters = 20,
}) => {
  const [hoveredDefect, setHoveredDefect] = useState<DefectDetection | null>(null);

  const safeTotal = Math.max(totalLengthMeters, 1);
  const crawlerPosPercent = currentDistanceMeters != null
    ? Math.min(Math.max((currentDistanceMeters / safeTotal) * 100, 0), 100)
    : 0;

  const getDefectColor = (defectClass: string) => {
    const lower = defectClass.toLowerCase();
    switch (lower) {
      case 'rupture':
        return 'bg-status-critical border-status-critical text-white';
      case 'deformation':
        return 'bg-brand-orange border-brand-orange text-white';
      case 'misalignment':
        return 'bg-blue-600 border-blue-600 text-white';
      case 'obstacle':
        return 'bg-purple-600 border-purple-600 text-white';
      default:
        return 'bg-industrial-700 border-industrial-700 text-white';
    }
  };

  return (
    <Card variant="default" className="border-industrial-300">
      <CardHeader className="p-4 pb-2 border-b border-industrial-200 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Ruler className="w-4 h-4 text-brand-orange" />
          <CardTitle className="text-xs font-mono uppercase tracking-wider">
            Longitudinal Conduit Anomaly Timeline
          </CardTitle>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono text-industrial-600">
          <span>Range: 0.00 m - {safeTotal.toFixed(1)} m</span>
          <Badge variant="outline" isMono className="text-[10px]">
            {defects.length} Detected
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-6 space-y-4">
        {/* Pipe Track Visual Bar */}
        <div className="relative h-10 bg-industrial-100 border-2 border-industrial-800 rounded-sm flex items-center px-2">
          {/* Internal Pipe Bore Grid Lines */}
          <div className="absolute inset-x-0 h-px bg-industrial-300 top-1/2 -translate-y-1/2" />
          {[0.25, 0.5, 0.75].map((fraction) => (
            <div
              key={fraction}
              style={{ left: `${fraction * 100}%` }}
              className="absolute top-0 bottom-0 w-px bg-industrial-200 border-dashed"
            />
          ))}

          {/* Crawler Position Cursor */}
          {currentDistanceMeters != null && (
            <div
              style={{ left: `${crawlerPosPercent}%` }}
              className="absolute top-0 bottom-0 w-1 bg-brand-orange z-10 transition-all duration-300 shadow-sm"
              title={`Crawler Position: ${currentDistanceMeters.toFixed(2)} m`}
            >
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 w-2 h-2 rotate-45 bg-brand-orange" />
            </div>
          )}

          {/* Anomaly Marker Pins */}
          {defects.map((d, index) => {
            const distance = d.estimatedDistanceMeters ?? 0;
            const leftPct = Math.min(Math.max((distance / safeTotal) * 100, 2), 98);
            const colorClass = getDefectColor(d.defectClass);

            return (
              <button
                key={d.id || index}
                style={{ left: `${leftPct}%` }}
                onMouseEnter={() => setHoveredDefect(d)}
                onMouseLeave={() => setHoveredDefect(null)}
                className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full border-2 flex items-center justify-center font-mono text-[9px] font-bold shadow-sm transition-transform hover:scale-125 z-20 focus:outline-none ${colorClass}`}
                aria-label={`Defect ${d.defectClass} at ${distance.toFixed(2)} m`}
              >
                {index + 1}
              </button>
            );
          })}
        </div>

        {/* Distance Scale Marks */}
        <div className="flex justify-between text-[10px] font-mono text-industrial-500 px-1">
          <span>0.0 m (Conduit Invert)</span>
          <span>{(safeTotal * 0.25).toFixed(1)} m</span>
          <span>{(safeTotal * 0.5).toFixed(1)} m</span>
          <span>{(safeTotal * 0.75).toFixed(1)} m</span>
          <span>{safeTotal.toFixed(1)} m (Target Access Point)</span>
        </div>

        {/* Hovered Anomaly Detail Callout */}
        {hoveredDefect ? (
          <div className="p-2.5 bg-industrial-50 border border-industrial-300 rounded-sm flex items-center justify-between text-xs font-mono animate-in fade-in duration-100">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${getDefectColor(hoveredDefect.defectClass)}`} />
              <span className="font-bold text-industrial-900">{hoveredDefect.defectClass}</span>
              <span className="text-industrial-500">at {(hoveredDefect.estimatedDistanceMeters ?? 0).toFixed(2)} m</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-industrial-600">
                Confidence: {hoveredDefect.confidence != null ? `${(hoveredDefect.confidence * 100).toFixed(1)}%` : '--'}
              </span>
              <Badge variant="outline" isMono className="text-[10px]">
                {hoveredDefect.reviewStatus}
              </Badge>
            </div>
          </div>
        ) : (
          <div className="text-[11px] font-mono text-industrial-500 flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-industrial-400" />
            <span>Hover over numbered pins to inspect spatial anomaly properties along the pipeline bore.</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
