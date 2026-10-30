import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { SYSTEM_INFO } from '@/constants/system';
import { Badge } from '@/components/ui/Badge';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import {
  LayoutDashboard,
  Eye,
  Sliders,
  Activity,
  AlertOctagon,
  History,
  FileText,
  Settings,
  Home,
} from 'lucide-react';

export const Navigation: FC = () => {
  const navItems = [
    { label: 'Overview', path: ROUTES.DASHBOARD.ROOT, icon: LayoutDashboard, end: true },
    { label: 'Inspection', path: ROUTES.DASHBOARD.INSPECTION, icon: Eye },
    { label: 'Vehicle', path: ROUTES.DASHBOARD.VEHICLE, icon: Sliders },
    { label: 'Telemetry', path: ROUTES.DASHBOARD.TELEMETRY, icon: Activity },
    { label: 'Defects', path: ROUTES.DASHBOARD.DEFECTS, icon: AlertOctagon },
    { label: 'History', path: ROUTES.DASHBOARD.HISTORY, icon: History },
    { label: 'Reports', path: ROUTES.DASHBOARD.REPORTS, icon: FileText },
    { label: 'Settings', path: ROUTES.DASHBOARD.SETTINGS, icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-industrial-200">
      {/* Top Industrial Bar */}
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Brand & System Tag */}
          <div className="flex items-center gap-3">
            <NavLink to={ROUTES.HOME} className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange border border-industrial-900 group-hover:border-brand-orange transition-colors">
                <svg className="w-5 h-5" viewBox="0 0 32 32" fill="none">
                  <circle cx="16" cy="16" r="10" stroke="#CBD5E1" strokeWidth="2.5" />
                  <circle cx="16" cy="16" r="5" stroke="#EA580C" strokeWidth="2" />
                  <line x1="16" y1="2" x2="16" y2="7" stroke="#EA580C" strokeWidth="2" />
                  <line x1="16" y1="25" x2="16" y2="30" stroke="#EA580C" strokeWidth="2" />
                  <line x1="2" y1="16" x2="7" y2="16" stroke="#EA580C" strokeWidth="2" />
                  <line x1="25" y1="16" x2="30" y2="16" stroke="#EA580C" strokeWidth="2" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold tracking-wider uppercase text-industrial-900 leading-tight">
                  {SYSTEM_INFO.NAME}
                </span>
                <span className="text-[10px] uppercase font-mono text-industrial-500 tracking-wider">
                  Robotic Inspection System
                </span>
              </div>
            </NavLink>

            <div className="hidden sm:block h-4 w-px bg-industrial-200" />
            <Badge variant="brand" isMono className="hidden sm:inline-flex">
              Stage 1
            </Badge>
          </div>

          {/* Right Header Status */}
          <div className="flex items-center gap-4">
            <NavLink
              to={ROUTES.HOME}
              className={({ isActive }) =>
                `text-xs font-semibold px-2.5 py-1.5 rounded-sm border transition-colors flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-white text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <Home className="w-3.5 h-3.5" />
              <span>Landing</span>
            </NavLink>

            <div className="h-4 w-px bg-industrial-200 hidden md:block" />

            <div className="hidden md:flex items-center gap-2">
              <StatusIndicator status="healthy" label="Core Ready" />
            </div>
          </div>
        </div>
      </div>

      {/* Sub-Navigation for Dashboard Routes */}
      <div className="bg-industrial-50 border-t border-industrial-200 overflow-x-auto">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-1 py-1.5" aria-label="Dashboard Navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.end}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-sm border whitespace-nowrap transition-colors select-none ${
                      isActive
                        ? 'bg-industrial-900 text-white border-industrial-900 shadow-industrial-sm'
                        : 'bg-transparent text-industrial-600 border-transparent hover:bg-white hover:text-industrial-900 hover:border-industrial-200'
                    }`
                  }
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};
