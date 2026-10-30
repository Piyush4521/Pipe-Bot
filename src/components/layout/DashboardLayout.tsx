import { useState, useMemo, type FC } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { DashboardSidebar } from './DashboardSidebar';
import { DashboardHeader } from './DashboardHeader';
import { DashboardMobileNav } from './DashboardMobileNav';
import { DemoModeBanner } from '@/components/shared/DemoModeBanner';
import { ROUTES } from '@/constants/routes';
import { SYSTEM_INFO } from '@/constants/system';

export const DashboardLayout: FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();

  // Derive title & breadcrumb based on current pathname
  const { title, breadcrumbs } = useMemo(() => {
    const path = location.pathname;

    if (path === ROUTES.DASHBOARD.INSPECTION) {
      return {
        title: 'Live Inspection Workspace',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.VEHICLE) {
      return {
        title: 'Vehicle Propulsion Control',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.TELEMETRY) {
      return {
        title: 'Sensor & Encoder Telemetry',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.DEFECTS) {
      return {
        title: 'Defect Management & Classification',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.HISTORY) {
      return {
        title: 'Inspection Mission History',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.REPORTS) {
      return {
        title: 'Inspection Reports & Compliance',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }
    if (path === ROUTES.DASHBOARD.SETTINGS) {
      return {
        title: 'System & Hardware Configuration',
        breadcrumbs: [{ label: 'Dashboard', path: ROUTES.DASHBOARD.ROOT }],
      };
    }

    return {
      title: 'Operational Console Overview',
      breadcrumbs: [],
    };
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex bg-industrial-50 text-industrial-900">
      {/* Desktop Sidebar */}
      <DashboardSidebar
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed(!collapsed)}
      />

      {/* Mobile Drawer */}
      <DashboardMobileNav
        isOpen={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
      />

      {/* Main Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader
          pageTitle={title}
          breadcrumbs={breadcrumbs}
          onOpenMobileNav={() => setMobileNavOpen(true)}
        />

        <DemoModeBanner />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-screen-2xl w-full mx-auto">
          <Outlet />
        </main>

        {/* Dashboard Technical Footer */}
        <footer className="bg-white border-t border-industrial-200 py-3 px-4 sm:px-6 lg:px-8 text-xs text-industrial-500">
          <div className="max-w-screen-2xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-industrial-800">{SYSTEM_INFO.NAME}</span>
              <span>/</span>
              <span>{SYSTEM_INFO.CURRENT_STAGE}</span>
            </div>
            <div className="font-mono text-[11px] text-industrial-400">
              Hardware: {SYSTEM_INFO.SPECIFICATION.CONTROLLER} | {SYSTEM_INFO.SPECIFICATION.CAMERA} | {SYSTEM_INFO.SPECIFICATION.MOTOR_DRIVER}
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

