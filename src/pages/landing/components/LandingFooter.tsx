import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { SYSTEM_INFO } from '@/constants/system';
import { Badge } from '@/components/ui/Badge';
import { ArrowUpRight, ChevronUp } from 'lucide-react';

export const LandingFooter: FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      const navOffset = 70;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;
      window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-white border-t border-industrial-200 text-industrial-600 text-xs">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12">
          {/* Brand Column (Spans 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange border border-industrial-900 shrink-0">
                <svg className="w-5 h-5" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                  <circle cx="16" cy="16" r="10" stroke="#CBD5E1" strokeWidth="2.5" />
                  <circle cx="16" cy="16" r="5" stroke="#EA580C" strokeWidth="2" />
                  <line x1="16" y1="2" x2="16" y2="7" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                  <line x1="16" y1="25" x2="16" y2="30" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                  <line x1="2" y1="16" x2="7" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                  <line x1="25" y1="16" x2="30" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                </svg>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold tracking-wider uppercase text-industrial-900 leading-none">
                    {SYSTEM_INFO.NAME}
                  </span>
                  <Badge variant="brand" isMono className="text-[10px] py-0 px-1.5">
                    Prototype
                  </Badge>
                </div>
                <span className="text-[10px] uppercase font-mono text-industrial-500 tracking-wider mt-0.5">
                  Robotic Pipeline Inspection
                </span>
              </div>
            </div>

            <p className="text-industrial-600 text-xs leading-relaxed max-w-sm">
              An AI-powered robotic platform engineered to inspect internal structural conditions of rigid PVC conduits, combining dual optical odometry with server-side computer vision defect classification.
            </p>

            <div className="pt-2 font-mono text-[11px] text-industrial-500 space-y-1">
              <div>Hardware: Dual ESP32 (WROOM-32 + AI Thinker CAM)</div>
              <div>Vision: OV2640 Image Sensor + Ultralytics YOLO</div>
            </div>
          </div>

          {/* Column 2: Landing Navigation */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-industrial-900">
              Navigation
            </h4>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => scrollToSection('hero')}
                  className="hover:text-brand-orange transition-colors"
                >
                  System Home
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection('overview')}
                  className="hover:text-brand-orange transition-colors"
                >
                  Platform Overview
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection('process')}
                  className="hover:text-brand-orange transition-colors"
                >
                  Inspection Process
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection('architecture')}
                  className="hover:text-brand-orange transition-colors"
                >
                  System Architecture
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection('capabilities')}
                  className="hover:text-brand-orange transition-colors"
                >
                  Defect Classifications
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection('technology')}
                  className="hover:text-brand-orange transition-colors"
                >
                  Technology Stack
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Dashboard Views */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-industrial-900">
              Operator Console
            </h4>
            <ul className="space-y-2">
              <li>
                <NavLink to={ROUTES.DASHBOARD.ROOT} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Dashboard Overview</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
              <li>
                <NavLink to={ROUTES.DASHBOARD.INSPECTION} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Live Inspection</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
              <li>
                <NavLink to={ROUTES.DASHBOARD.VEHICLE} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Vehicle Control</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
              <li>
                <NavLink to={ROUTES.DASHBOARD.TELEMETRY} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Odometry Telemetry</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
              <li>
                <NavLink to={ROUTES.DASHBOARD.DEFECTS} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Defect Catalogue</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
              <li>
                <NavLink to={ROUTES.DASHBOARD.REPORTS} className="hover:text-brand-orange transition-colors flex items-center gap-1">
                  <span>Inspection Reports</span>
                  <ArrowUpRight className="w-3 h-3 opacity-60" />
                </NavLink>
              </li>
            </ul>
          </div>

          {/* Column 4: Legal & Notice */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-industrial-900">
              Project Governance
            </h4>
            <ul className="space-y-2 text-industrial-600">
              <li>
                <NavLink
                  to={ROUTES.PRIVACY}
                  className="hover:text-brand-orange transition-colors flex items-center gap-1.5"
                >
                  <span className="text-industrial-400 font-mono text-[10px]">[Draft]</span>
                  <span>Privacy Policy</span>
                </NavLink>
              </li>
              <li>
                <NavLink
                  to={ROUTES.TERMS}
                  className="hover:text-brand-orange transition-colors flex items-center gap-1.5"
                >
                  <span className="text-industrial-400 font-mono text-[10px]">[Draft]</span>
                  <span>Terms of Use</span>
                </NavLink>
              </li>
              <li className="flex items-center gap-1.5 text-industrial-500">
                <span className="text-industrial-400 font-mono text-[10px]">[Draft]</span>
                <span>Conduit Safety Protocol</span>
              </li>
              <li className="pt-2 border-t border-industrial-100">
                <Badge variant="outline" isMono className="text-[10px] text-brand-orange border-brand-orange/30">
                  Stage 5 Release Ready
                </Badge>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Horizontal Bar */}
        <div className="mt-12 pt-6 border-t border-industrial-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] font-mono text-industrial-500">
          <div>
            PipeBot Project. Developed for engineering research and evaluation.
          </div>

          <div className="flex items-center gap-4">
            <span>Client: React + Vite + TS</span>
            <span>•</span>
            <button
              onClick={scrollToTop}
              className="hover:text-industrial-900 transition-colors flex items-center gap-1"
              aria-label="Back to top"
            >
              <span>Back to Top</span>
              <ChevronUp className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};

