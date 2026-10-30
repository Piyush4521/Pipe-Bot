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
  X,
} from 'lucide-react';

interface DashboardMobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DashboardMobileNav: FC<DashboardMobileNavProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const navItems = [
    { label: 'Overview', path: ROUTES.DASHBOARD.ROOT, icon: LayoutDashboard, end: true },
    { label: 'Live Inspection', path: ROUTES.DASHBOARD.INSPECTION, icon: Eye },
    { label: 'Vehicle Control', path: ROUTES.DASHBOARD.VEHICLE, icon: Sliders },
    { label: 'Telemetry', path: ROUTES.DASHBOARD.TELEMETRY, icon: Activity },
    { label: 'Defects', path: ROUTES.DASHBOARD.DEFECTS, icon: AlertOctagon },
    { label: 'Inspection History', path: ROUTES.DASHBOARD.HISTORY, icon: History },
    { label: 'Reports', path: ROUTES.DASHBOARD.REPORTS, icon: FileText },
    { label: 'Settings', path: ROUTES.DASHBOARD.SETTINGS, icon: Settings },
  ];

  return (
    <div className="fixed inset-0 z-50 lg:hidden flex">
      {/* Dimmed Backdrop */}
      <div
        className="fixed inset-0 bg-industrial-950/50 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Panel */}
      <div className="relative w-72 max-w-[80vw] bg-white h-full flex flex-col shadow-xl z-10 border-r border-industrial-200">
        {/* Drawer Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-industrial-200">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange">
              <svg className="w-4 h-4" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="8" stroke="#EA580C" strokeWidth="2" />
              </svg>
            </div>
            <span className="font-bold text-sm uppercase tracking-wider text-industrial-900">
              {SYSTEM_INFO.NAME}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-sm text-industrial-500 hover:text-industrial-900 hover:bg-industrial-100"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Links */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Mobile Navigation">
          <div className="px-3 pb-2 text-[10px] font-mono uppercase font-bold text-industrial-400 tracking-wider">
            Operator Modules
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.end}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-sm border transition-colors ${
                    isActive
                      ? 'bg-industrial-900 text-white border-industrial-900 shadow-industrial-sm'
                      : 'bg-transparent text-industrial-700 border-transparent hover:bg-industrial-100'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Drawer Footer */}
        <div className="p-4 border-t border-industrial-200 bg-industrial-50 space-y-3">
          <div className="p-2.5 bg-white border border-industrial-200 rounded-sm space-y-1 text-xs">
            <div className="flex items-center justify-between font-mono text-[11px]">
              <span className="text-industrial-500">Status</span>
              <Badge variant="outline" isMono className="text-[10px]">Prototype</Badge>
            </div>
            <StatusIndicator status="offline" label="Hardware: Disconnected" size="sm" />
          </div>

          <NavLink
            to={ROUTES.HOME}
            onClick={onClose}
            className="flex items-center justify-center gap-2 w-full py-2 px-3 text-xs font-semibold text-industrial-800 bg-white border border-industrial-300 rounded-sm hover:bg-industrial-100 transition-colors"
          >
            <Home className="w-4 h-4 text-industrial-500" />
            <span>Return to Public Site</span>
          </NavLink>
        </div>
      </div>
    </div>
  );
};

