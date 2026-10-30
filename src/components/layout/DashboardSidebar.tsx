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
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface DashboardSidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const DashboardSidebar: FC<DashboardSidebarProps> = ({
  collapsed,
  onToggleCollapse,
}) => {
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
    <aside
      className={`hidden lg:flex flex-col bg-white border-r border-industrial-200 transition-all duration-200 select-none z-30 shrink-0 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-industrial-200">
        {!collapsed ? (
          <NavLink to={ROUTES.HOME} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange border border-industrial-900 group-hover:border-brand-orange transition-colors shrink-0">
              <svg className="w-4 h-4" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <circle cx="16" cy="16" r="10" stroke="#CBD5E1" strokeWidth="2.5" />
                <circle cx="16" cy="16" r="5" stroke="#EA580C" strokeWidth="2" />
                <line x1="16" y1="2" x2="16" y2="7" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="16" y1="25" x2="16" y2="30" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="2" y1="16" x2="7" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="25" y1="16" x2="30" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold tracking-wider uppercase text-industrial-900 leading-none">
                {SYSTEM_INFO.NAME}
              </span>
              <span className="text-[10px] uppercase font-mono text-industrial-500 tracking-wider mt-0.5">
                Operator Console
              </span>
            </div>
          </NavLink>
        ) : (
          <div className="mx-auto">
            <div className="w-8 h-8 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange border border-industrial-900">
              <svg className="w-4 h-4" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="8" stroke="#EA580C" strokeWidth="2" />
              </svg>
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-sm text-industrial-500 hover:text-industrial-900 hover:bg-industrial-100 transition-colors"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          aria-label={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {!collapsed && (
          <div className="px-3 pb-2 text-[10px] font-mono uppercase font-bold text-industrial-400 tracking-wider">
            Navigation Modules
          </div>
        )}

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              title={collapsed ? item.label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-sm border transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900 shadow-industrial-sm'
                    : 'bg-transparent text-industrial-700 border-transparent hover:bg-industrial-100 hover:text-industrial-950'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </div>

      {/* Bottom Status & Landing Return */}
      <div className="p-3 border-t border-industrial-200 bg-industrial-50 space-y-2">
        {!collapsed ? (
          <>
            <div className="p-2.5 bg-white border border-industrial-200 rounded-sm space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="text-industrial-500">System State</span>
                <Badge variant="outline" isMono className="text-[10px]">
                  Prototype
                </Badge>
              </div>
              <StatusIndicator status="offline" label="Hardware: Disconnected" size="sm" />
            </div>

            <NavLink
              to={ROUTES.HOME}
              className="flex items-center justify-center gap-2 w-full py-1.5 px-3 text-xs font-medium text-industrial-700 hover:text-industrial-900 hover:bg-white border border-transparent hover:border-industrial-200 rounded-sm transition-colors"
            >
              <Home className="w-3.5 h-3.5 text-industrial-500" />
              <span>Back to Public Site</span>
            </NavLink>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <NavLink
              to={ROUTES.HOME}
              title="Return to Public Site"
              className="p-2 text-industrial-600 hover:text-industrial-900 hover:bg-white rounded-sm"
            >
              <Home className="w-4 h-4" />
            </NavLink>
          </div>
        )}
      </div>
    </aside>
  );
};

