import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import {
  ArrowRight,
  ChevronDown,
} from 'lucide-react';

export const HeroSection: FC = () => {
  const scrollToProcess = () => {
    const el = document.getElementById('process');
    if (el) {
      const navOffset = 70;
      const elementPosition = el.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;
      window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="relative pt-8 pb-16 lg:pt-14 lg:pb-24 border-b border-industrial-200 overflow-hidden bg-white">
      {/* Background Subtle Technical Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(#0F172A 1px, transparent 1px)`,
          backgroundSize: '24px 24px',
        }}
      />

      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          {/* Left Column: Editorial Information & Action */}
          <div className="lg:col-span-6 space-y-6">
            {/* Status & Scope Pill */}
            <div className="inline-flex items-center gap-2 p-1 pr-3 bg-industrial-100 border border-industrial-300 rounded-sm">
              <span className="px-2 py-0.5 bg-industrial-900 text-white font-mono text-[11px] uppercase tracking-wider rounded-sm font-semibold">
                Prototype
              </span>
              <span className="text-xs font-medium text-industrial-700">
                Robotic PVC Pipeline Inspection Platform
              </span>
            </div>

            {/* Main Editorial Headline */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-industrial-950 leading-[1.12]">
              Intelligent Inspection Inside Every Pipeline.
            </h1>

            {/* Supporting Copy */}
            <p className="text-base sm:text-lg text-industrial-600 leading-relaxed max-w-xl">
              PipeBot combines robotic mobility, internal visual inspection and AI-based defect detection to help identify pipeline damage and estimate its location.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
              <NavLink to={ROUTES.DASHBOARD.ROOT}>
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full sm:w-auto"
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                >
                  Explore Inspection Platform
                </Button>
              </NavLink>

              <Button
                variant="outline"
                size="lg"
                onClick={scrollToProcess}
                rightIcon={<ChevronDown className="w-4 h-4" />}
              >
                How It Works
              </Button>
            </div>

            {/* Engineering Highlights Bento Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6 border-t border-industrial-200">
              <div className="space-y-1">
                <span className="text-[11px] font-mono uppercase text-industrial-500 block">Conduit Target</span>
                <span className="text-sm font-bold text-industrial-900 font-mono">150 - 300 mm</span>
                <span className="text-[11px] text-industrial-500 block">Rigid PVC Pipes</span>
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-mono uppercase text-industrial-500 block">Controller</span>
                <span className="text-sm font-bold text-industrial-900 font-mono">ESP32 Dual</span>
                <span className="text-[11px] text-industrial-500 block">WROOM + CAM</span>
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-mono uppercase text-industrial-500 block">AI Inference</span>
                <span className="text-sm font-bold text-industrial-900 font-mono">Custom YOLO</span>
                <span className="text-[11px] text-industrial-500 block">Server Processing</span>
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-mono uppercase text-industrial-500 block">Odometry</span>
                <span className="text-sm font-bold text-industrial-900 font-mono">Dual Encoders</span>
                <span className="text-[11px] text-industrial-500 block">Distance Ticks</span>
              </div>
            </div>
          </div>

          {/* Right Column: Custom Technical Vector Schematic */}
          <div className="lg:col-span-6">
            <Card variant="raised" className="overflow-hidden border-industrial-300">
              {/* Card Technical Header */}
              <div className="px-4 py-2.5 bg-industrial-900 text-white flex items-center justify-between text-xs font-mono border-b border-industrial-900">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-brand-orange rounded-full animate-pulse" />
                  <span className="font-semibold tracking-wider uppercase">Fig 1.0 | Longitudinal In-Pipe Schematic</span>
                </div>
                <Badge variant="outline" isMono className="text-white border-industrial-700 bg-industrial-800 text-[10px]">
                  PVC 200mm Dia
                </Badge>
              </div>

              {/* Vector SVG Technical Illustration */}
              <div className="p-4 sm:p-6 bg-industrial-50">
                <svg
                  viewBox="0 0 680 400"
                  className="w-full h-auto select-none"
                  xmlns="http://www.w3.org/2000/svg"
                  role="img"
                  aria-label="Schematic illustration of the PipeBot four-wheel crawler inside a PVC pipe with camera field of view and optical encoders"
                >
                  <defs>
                    {/* Pipe Hatch Pattern */}
                    <pattern id="pipeHatch" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                      <line x1="0" y1="0" x2="0" y2="8" stroke="#CBD5E1" strokeWidth="1" />
                    </pattern>
                    {/* Camera FOV Gradient */}
                    <linearGradient id="camFov" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#EA580C" stopOpacity="0.35" />
                      <stop offset="85%" stopColor="#EA580C" stopOpacity="0.08" />
                      <stop offset="100%" stopColor="#EA580C" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>

                  {/* Upper PVC Pipe Wall */}
                  <rect x="20" y="40" width="640" height="28" fill="url(#pipeHatch)" stroke="#94A3B8" strokeWidth="1.5" />
                  <line x1="20" y1="68" x2="660" y2="68" stroke="#0F172A" strokeWidth="2.5" />
                  <text x="35" y="58" fill="#475569" fontSize="10" fontFamily="JetBrains Mono, monospace" fontWeight="600">
                    PVC PIPE UPPER WALL : SCHEDULE 40
                  </text>

                  {/* Lower PVC Pipe Wall */}
                  <rect x="20" y="332" width="640" height="28" fill="url(#pipeHatch)" stroke="#94A3B8" strokeWidth="1.5" />
                  <line x1="20" y1="332" x2="660" y2="332" stroke="#0F172A" strokeWidth="2.5" />
                  <text x="35" y="350" fill="#475569" fontSize="10" fontFamily="JetBrains Mono, monospace" fontWeight="600">
                    PIPE INVERT : ROLLING SURFACE
                  </text>

                  {/* Internal Pipeline Centerline Guide */}
                  <line x1="20" y1="200" x2="660" y2="200" stroke="#CBD5E1" strokeWidth="1" strokeDasharray="6,4" />
                  <text x="540" y="194" fill="#94A3B8" fontSize="9" fontFamily="JetBrains Mono, monospace">
                    PIPE CENTERLINE
                  </text>

                  {/* Pipe Dimension Callout */}
                  <line x1="30" y1="72" x2="30" y2="328" stroke="#64748B" strokeWidth="1" />
                  <line x1="24" y1="72" x2="36" y2="72" stroke="#64748B" strokeWidth="1" />
                  <line x1="24" y1="328" x2="36" y2="328" stroke="#64748B" strokeWidth="1" />
                  <text x="38" y="204" fill="#475569" fontSize="10" fontFamily="JetBrains Mono, monospace" fontWeight="600">
                    Ø 200 mm ID
                  </text>

                  {/* Traversal Motion Arrow */}
                  <line x1="210" y1="100" x2="330" y2="100" stroke="#EA580C" strokeWidth="2.5" markerEnd="url(#arrow)" />
                  <polygon points="330,96 342,100 330,104" fill="#EA580C" />
                  <text x="210" y="90" fill="#EA580C" fontSize="10" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    TRAVERSAL VECTOR (+X)
                  </text>

                  {/* CAMERA FIELD OF VIEW CONE */}
                  <polygon points="268,220 540,110 540,305" fill="url(#camFov)" stroke="#EA580C" strokeWidth="1" strokeDasharray="3,3" />

                  {/* Target Defect Bounding Box on Pipe Wall */}
                  <rect x="520" y="130" width="80" height="90" fill="#FEF2F2" fillOpacity="0.8" stroke="#DC2626" strokeWidth="2" strokeDasharray="4,2" />
                  <text x="526" y="145" fill="#DC2626" fontSize="9" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    DEFECT REGION
                  </text>
                  <line x1="535" y1="160" x2="585" y2="185" stroke="#DC2626" strokeWidth="2" />
                  <line x1="585" y1="185" x2="570" y2="210" stroke="#DC2626" strokeWidth="2" />
                  <text x="526" y="210" fill="#7F1D1D" fontSize="8" fontFamily="JetBrains Mono, monospace">
                    YOLO BOUNDING BOX
                  </text>

                  {/* --- ROBOTIC CRAWLER VEHICLE CHASSIS --- */}

                  {/* Rear Wheels */}
                  <rect x="100" y="275" width="45" height="57" rx="3" fill="#1E293B" stroke="#0F172A" strokeWidth="2" />
                  <line x1="105" y1="285" x2="140" y2="285" stroke="#64748B" strokeWidth="2" />
                  <line x1="105" y1="300" x2="140" y2="300" stroke="#64748B" strokeWidth="2" />
                  <line x1="105" y1="315" x2="140" y2="315" stroke="#64748B" strokeWidth="2" />

                  {/* Front Wheels */}
                  <rect x="220" y="275" width="45" height="57" rx="3" fill="#1E293B" stroke="#0F172A" strokeWidth="2" />
                  <line x1="225" y1="285" x2="260" y2="285" stroke="#64748B" strokeWidth="2" />
                  <line x1="225" y1="300" x2="260" y2="300" stroke="#64748B" strokeWidth="2" />
                  <line x1="225" y1="315" x2="260" y2="315" stroke="#64748B" strokeWidth="2" />

                  {/* Optical Wheel Encoder Disc near Front Wheel */}
                  <circle cx="242" cy="303" r="14" fill="#0F172A" stroke="#EA580C" strokeWidth="1.5" />
                  <circle cx="242" cy="303" r="4" fill="#EA580C" />
                  <line x1="242" y1="290" x2="242" y2="316" stroke="#EA580C" strokeWidth="1" strokeDasharray="2,2" />
                  <line x1="229" y1="303" x2="255" y2="303" stroke="#EA580C" strokeWidth="1" strokeDasharray="2,2" />

                  {/* Main Chassis Body */}
                  <rect x="110" y="235" width="150" height="50" rx="2" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2.5" />

                  {/* Internal Subsystem Indicators on Chassis */}
                  {/* Battery Compartment */}
                  <rect x="118" y="243" width="38" height="34" fill="#F1F3F5" stroke="#CBD5E1" strokeWidth="1" />
                  <text x="122" y="264" fill="#475569" fontSize="8" fontFamily="JetBrains Mono, monospace" fontWeight="600">
                    BATT
                  </text>

                  {/* ESP32-WROOM-32 Controller Compartment */}
                  <rect x="162" y="243" width="44" height="34" fill="#F1F3F5" stroke="#EA580C" strokeWidth="1.5" />
                  <text x="166" y="258" fill="#EA580C" fontSize="7.5" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    ESP32
                  </text>
                  <text x="166" y="269" fill="#0F172A" fontSize="7" fontFamily="JetBrains Mono, monospace">
                    WROOM
                  </text>

                  {/* MPU6050 IMU */}
                  <rect x="212" y="243" width="22" height="15" fill="#E2E8F0" stroke="#94A3B8" strokeWidth="1" />
                  <text x="214" y="254" fill="#0F172A" fontSize="6.5" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    IMU
                  </text>

                  {/* Camera Mast & ESP32-CAM Head */}
                  <path d="M 250 245 L 268 220" stroke="#0F172A" strokeWidth="3" />
                  {/* Camera Enclosure */}
                  <rect x="260" y="208" width="22" height="24" rx="2" fill="#0F172A" stroke="#EA580C" strokeWidth="1.5" />
                  {/* Lens */}
                  <circle cx="277" cy="220" r="5" fill="#EA580C" stroke="#FFFFFF" strokeWidth="1" />
                  {/* High Intensity LED Array */}
                  <circle cx="277" cy="212" r="1.5" fill="#FDE047" />
                  <circle cx="277" cy="228" r="1.5" fill="#FDE047" />

                  {/* --- TECHNICAL LABELS AND LEADER LINES --- */}
                  {/* Camera Callout */}
                  <line x1="275" y1="205" x2="310" y2="155" stroke="#0F172A" strokeWidth="1" />
                  <line x1="310" y1="155" x2="410" y2="155" stroke="#0F172A" strokeWidth="1" />
                  <text x="415" y="158" fill="#0F172A" fontSize="9" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    ESP32-CAM (OV2640 + LED ILLUMINATION)
                  </text>

                  {/* Encoder Callout */}
                  <line x1="242" y1="317" x2="242" y2="380" stroke="#EA580C" strokeWidth="1" />
                  <line x1="242" y1="380" x2="340" y2="380" stroke="#EA580C" strokeWidth="1" />
                  <text x="345" y="383" fill="#EA580C" fontSize="9" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    DUAL OPTICAL WHEEL ENCODERS (ODOMETRY TICKS)
                  </text>

                  {/* Controller Callout */}
                  <line x1="184" y1="243" x2="184" y2="175" stroke="#0F172A" strokeWidth="1" />
                  <line x1="184" y1="175" x2="110" y2="175" stroke="#0F172A" strokeWidth="1" />
                  <text x="45" y="172" fill="#0F172A" fontSize="9" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    ESP32-WROOM-32 (MOTOR + IMU)
                  </text>

                  {/* 4WD Wheels Callout */}
                  <line x1="120" y1="332" x2="120" y2="380" stroke="#64748B" strokeWidth="1" />
                  <line x1="120" y1="380" x2="80" y2="380" stroke="#64748B" strokeWidth="1" />
                  <text x="30" y="383" fill="#475569" fontSize="9" fontFamily="JetBrains Mono, monospace" fontWeight="700">
                    4WD HIGH-TRACTION TREAD
                  </text>
                </svg>
              </div>

              {/* Technical Caption Footer */}
              <div className="px-4 py-2 bg-industrial-100 border-t border-industrial-200 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-industrial-600 font-mono gap-1">
                <span>Vehicle: Dual ESP32 Subsystem Architecture</span>
                <span className="text-industrial-500">Camera FOV: 65° Conical Projection</span>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};
