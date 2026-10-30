import type { FC } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Info } from 'lucide-react';

export const DefectCapabilities: FC = () => {
  const defectClasses = [
    {
      id: 'deformation',
      name: 'Deformation',
      category: 'Structural Geometry Anomaly',
      description:
        'Radial flattening, ovalization, or cross-sectional crushing caused by uneven earth surcharge, heavy vehicle loading, or soil compaction settlement.',
      impact: 'Reduces conduit cross-sectional flow area; acts as an early precursor to structural wall collapse.',
      // Vector schematic: Circular pipe deformed into an oval
      svg: (
        <svg viewBox="0 0 200 120" className="w-full h-24 select-none" fill="none">
          {/* Reference True Circle */}
          <ellipse cx="100" cy="60" rx="46" ry="46" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="3,3" />
          {/* Deformed Oval Pipe */}
          <ellipse cx="100" cy="60" rx="55" ry="34" stroke="#0F172A" strokeWidth="2" fill="#F8F9FA" />
          {/* Vertical Compression Force Arrows */}
          <line x1="100" y1="8" x2="100" y2="22" stroke="#DC2626" strokeWidth="2" />
          <polygon points="97,20 100,26 103,20" fill="#DC2626" />
          <line x1="100" y1="112" x2="100" y2="98" stroke="#DC2626" strokeWidth="2" />
          <polygon points="97,100 100,94 103,100" fill="#DC2626" />
          {/* Dimension delta */}
          <text x="100" y="63" textAnchor="middle" fill="#EA580C" fontSize="8" fontFamily="JetBrains Mono, monospace" fontWeight="700">
            Δh: -26%
          </text>
        </svg>
      ),
    },
    {
      id: 'misalignment',
      name: 'Misalignment',
      category: 'Joint Connection Defect',
      description:
        'Longitudinal joint displacement, angular deflection, or axial separation between adjoining PVC pipe bell-and-spigot segments.',
      impact: 'Allows groundwater infiltration, exfiltration of effluent into surrounding soil, and root ingress.',
      // Vector schematic: Two offset pipe segments
      svg: (
        <svg viewBox="0 0 200 120" className="w-full h-24 select-none" fill="none">
          {/* Pipe Segment Left */}
          <rect x="25" y="32" width="65" height="56" fill="#F8F9FA" stroke="#0F172A" strokeWidth="2" />
          {/* Pipe Segment Right (Vertically Offset) */}
          <rect x="100" y="44" width="75" height="56" fill="#F8F9FA" stroke="#0F172A" strokeWidth="2" />
          {/* Gap / Joint Exposure */}
          <rect x="90" y="32" width="10" height="68" fill="#FEE2E2" stroke="#DC2626" strokeWidth="1.5" strokeDasharray="2,2" />
          {/* Offset Indicator */}
          <line x1="90" y1="32" x2="100" y2="32" stroke="#DC2626" strokeWidth="1.5" />
          <line x1="90" y1="44" x2="100" y2="44" stroke="#DC2626" strokeWidth="1.5" />
          <text x="100" y="24" textAnchor="middle" fill="#DC2626" fontSize="8" fontFamily="JetBrains Mono, monospace" fontWeight="700">
            JOINT DISPLACEMENT (Δy)
          </text>
        </svg>
      ),
    },
    {
      id: 'obstacle',
      name: 'Obstacle',
      category: 'Hydraulic Flow Restriction',
      description:
        'Internal flow obstruction resulting from sediment buildup, gravel deposits, intrusive foreign solids, or tree root penetration.',
      impact: 'Reduces volumetric conduit discharge capacity; induces upstream surcharge and sediment damming.',
      // Vector schematic: Pipe invert filled with sediment
      svg: (
        <svg viewBox="0 0 200 120" className="w-full h-24 select-none" fill="none">
          {/* Pipe Cross-Section */}
          <circle cx="100" cy="60" r="46" stroke="#0F172A" strokeWidth="2" fill="#F8F9FA" />
          {/* Bottom Sediment Fill */}
          <path d="M 58 78 Q 100 55 142 78 A 46 46 0 0 1 58 78 Z" fill="#E2E8F0" stroke="#64748B" strokeWidth="1.5" />
          {/* Debris / Root Objects */}
          <circle cx="90" cy="88" r="5" fill="#475569" />
          <circle cx="108" cy="85" r="7" fill="#334155" />
          <circle cx="122" cy="92" r="4" fill="#475569" />
          <text x="100" y="50" textAnchor="middle" fill="#D97706" fontSize="8" fontFamily="JetBrains Mono, monospace" fontWeight="700">
            AREA BLOCKAGE: ~38%
          </text>
        </svg>
      ),
    },
    {
      id: 'rupture',
      name: 'Rupture',
      category: 'Critical Wall Failure',
      description:
        'Through-wall structural fractures, longitudinal pipe body splits, brittle impact punctures, or severe mechanical shearing.',
      impact: 'Complete structural failure requiring urgent localized excavation or trenchless sleeve rehabilitation.',
      // Vector schematic: Jagged fracture in pipe wall
      svg: (
        <svg viewBox="0 0 200 120" className="w-full h-24 select-none" fill="none">
          {/* Pipe Section */}
          <rect x="30" y="30" width="140" height="60" fill="#F8F9FA" stroke="#0F172A" strokeWidth="2" />
          {/* Jagged Crack Path */}
          <path d="M 85 30 L 92 48 L 86 62 L 105 75 L 98 90" stroke="#DC2626" strokeWidth="2.5" strokeLinejoin="bevel" fill="none" />
          {/* Crack Branching */}
          <path d="M 86 62 L 115 58" stroke="#DC2626" strokeWidth="1.5" fill="none" />
          {/* Warning Reticle */}
          <rect x="75" y="40" width="45" height="42" fill="none" stroke="#DC2626" strokeWidth="1" strokeDasharray="2,2" />
          <text x="100" y="22" textAnchor="middle" fill="#DC2626" fontSize="8" fontFamily="JetBrains Mono, monospace" fontWeight="700">
            WALL FRACTURE / CRACK
          </text>
        </svg>
      ),
    },
  ];

  return (
    <section id="capabilities" className="py-16 lg:py-24 bg-white border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                04 // Computer Vision Targets
              </span>
              <Badge variant="outline" isMono>Dataset Defect Classes</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              Target Defect Classifications
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              The four primary structural and operational anomaly categories configured for detection and bounding box localization within the YOLO inference pipeline.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Model: Custom Ultralytics YOLO Architecture
          </div>
        </div>

        {/* 4 Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {defectClasses.map((defect) => (
            <Card key={defect.id} variant="raised" className="border-industrial-300 flex flex-col justify-between">
              <div>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs uppercase font-bold text-industrial-500">
                      Class: {defect.id}
                    </span>
                    <Badge variant="default" isMono className="text-[10px]">
                      Target
                    </Badge>
                  </div>
                  <CardTitle className="text-base mt-1">{defect.name}</CardTitle>
                  <span className="font-mono text-[11px] text-brand-orange block font-medium">
                    {defect.category}
                  </span>
                </CardHeader>

                {/* Abstract Vector Diagram */}
                <div className="p-3 bg-industrial-100 border-y border-industrial-200 my-2">
                  {defect.svg}
                </div>

                <CardContent className="pt-2 text-xs text-industrial-600 space-y-2 leading-relaxed">
                  <p>{defect.description}</p>
                </CardContent>
              </div>

              <div className="p-4 bg-industrial-50 border-t border-industrial-200 text-xs">
                <span className="font-mono text-[11px] font-bold text-industrial-900 block mb-0.5">
                  Engineering Impact:
                </span>
                <p className="text-industrial-600 text-[11px] leading-normal">{defect.impact}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Rigorous Engineering Notice */}
        <div className="mt-10 p-5 bg-industrial-100 border border-industrial-300 rounded-sm">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0 mt-0.5">
              <Info className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-industrial-900 uppercase tracking-wide">
                Model Training & Validation Notice
              </h3>
              <p className="text-xs text-industrial-700 leading-relaxed">
                The PipeBot defect detection system is an active engineering research platform. Real-world accuracy and bounding box precision depend on training set diversity, lighting consistency, camera lens cleanliness, and wet PVC wall reflectivity. Detection output is intended as an operator decision-support tool, not as an autonomous certification mechanism.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
