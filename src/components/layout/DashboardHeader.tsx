import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useAppMode, useSystemStatus } from '@/app/providers/AppContext';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import {
  Menu,
  Home,
  ChevronRight,
  Sparkles,
  PowerOff,
  RefreshCw,
  Server,
} from 'lucide-react';

interface DashboardHeaderProps {
  pageTitle: string;
  onOpenMobileNav: () => void;
  breadcrumbs?: { label: string; path?: string }[];
}

export const DashboardHeader: FC<DashboardHeaderProps> = ({
  pageTitle,
  onOpenMobileNav,
  breadcrumbs = [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
}) => {
  const { isDemoMode, toggleDemoMode } = useAppMode();
  const { systemStatus, backendOnline, isRefreshing, refreshData } = useSystemStatus();

  return (
    <header className="h-16 bg-white border-b border-industrial-200 sticky top-0 z-20 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileNav}
          className="lg:hidden p-2 text-industrial-700 hover:bg-industrial-100 border border-industrial-300 rounded-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-orange"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex flex-col">
          {/* Breadcrumb row */}
          <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-[11px] font-mono text-industrial-500">
            {breadcrumbs.map((crumb, idx) => (
              <span key={idx} className="flex items-center gap-1.5">
                {crumb.path ? (
                  <NavLink to={crumb.path} className="hover:text-industrial-900 transition-colors">
                    {crumb.label}
                  </NavLink>
                ) : (
                  <span className="text-industrial-700">{crumb.label}</span>
                )}
                {idx < breadcrumbs.length - 1 && <ChevronRight className="w-3 h-3 text-industrial-400" />}
              </span>
            ))}
            <ChevronRight className="w-3 h-3 text-industrial-400" />
            <span className="text-industrial-900 font-semibold">{pageTitle}</span>
          </nav>

          <h1 className="text-base sm:text-lg font-bold text-industrial-950 tracking-tight leading-none mt-0.5">
            {pageTitle}
          </h1>
        </div>
      </div>

      {/* Right: Refresh, Demo Mode Toggle, Status & Landing Link */}
      <div className="flex items-center gap-2.5">
        {/* Sync / Refresh Trigger */}
        <button
          onClick={() => refreshData()}
          disabled={isRefreshing || isDemoMode}
          title="Query latest backend status and sync active database state"
          className="p-1.5 border border-industrial-200 rounded-sm text-industrial-600 hover:bg-industrial-100 hover:text-industrial-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-1 focus:ring-brand-orange"
          aria-label="Sync backend data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-brand-orange' : ''}`} />
        </button>

        {/* Controlled Demo Mode Toggle */}
        <Button
          variant={isDemoMode ? 'danger' : 'outline'}
          size="sm"
          onClick={toggleDemoMode}
          leftIcon={isDemoMode ? <PowerOff className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5 text-brand-orange" />}
          className="text-xs"
          title={isDemoMode ? 'Exit Demo Mode and return to real disconnected states' : 'Enable Demo Mode to preview dashboard with isolated sample records'}
        >
          {isDemoMode ? 'Exit Demo' : 'Demo Mode'}
        </Button>

        {/* Backend Connectivity Indicator */}
        <div className="hidden md:flex items-center gap-2 p-1.5 px-2.5 bg-industrial-100 border border-industrial-200 rounded-sm">
          <Server className="w-3.5 h-3.5 text-industrial-600" />
          <StatusIndicator
            status={isDemoMode || backendOnline || systemStatus.backend === 'connected' ? 'healthy' : 'offline'}
            size="sm"
            label={
              isDemoMode
                ? 'Backend: Demo Broker'
                : backendOnline || systemStatus.backend === 'connected'
                ? 'Backend: Online'
                : 'Backend: Offline'
            }
          />
        </div>

        {/* Hardware Status indicator */}
        <div className="hidden sm:flex items-center gap-3 p-1.5 px-3 bg-industrial-100 border border-industrial-200 rounded-sm">
          <StatusIndicator
            status={systemStatus.hardware === 'connected' ? 'healthy' : 'offline'}
            size="sm"
            label={systemStatus.hardware === 'connected' ? 'Hardware: Linked' : 'Hardware: Disconnected'}
          />
          <div className="h-3 w-px bg-industrial-300" />
          <Badge
            variant={isDemoMode ? 'brand' : 'outline'}
            isMono
            className="text-[10px] py-0"
          >
            {isDemoMode ? 'DEMO' : 'LIVE'}
          </Badge>
        </div>

        {/* Link back to public site */}
        <NavLink
          to={ROUTES.HOME}
          className="p-2 border border-industrial-200 rounded-sm text-industrial-700 hover:bg-industrial-100 hover:text-industrial-900 transition-colors flex items-center gap-1.5 text-xs font-medium"
          title="Return to Public Site"
        >
          <Home className="w-4 h-4" />
          <span className="hidden lg:inline">Public Site</span>
        </NavLink>
      </div>
    </header>
  );
};
