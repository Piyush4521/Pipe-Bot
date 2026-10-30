import { createBrowserRouter } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ROUTES } from '@/constants/routes';

// Pages
import { LandingPage } from '@/pages/landing/LandingPage';
import { PrivacyPage } from '@/pages/legal/PrivacyPage';
import { TermsPage } from '@/pages/legal/TermsPage';
import { OverviewPage } from '@/pages/dashboard/OverviewPage';
import { InspectionPage } from '@/pages/dashboard/InspectionPage';
import { VehiclePage } from '@/pages/dashboard/VehiclePage';
import { TelemetryPage } from '@/pages/dashboard/TelemetryPage';
import { DefectsPage } from '@/pages/dashboard/DefectsPage';
import { HistoryPage } from '@/pages/dashboard/HistoryPage';
import { ReportsPage } from '@/pages/dashboard/ReportsPage';
import { SettingsPage } from '@/pages/dashboard/SettingsPage';
import { NotFoundPage } from '@/pages/not-found/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: ROUTES.HOME,
    element: <LandingPage />,
  },
  {
    path: ROUTES.PRIVACY,
    element: <PrivacyPage />,
  },
  {
    path: ROUTES.TERMS,
    element: <TermsPage />,
  },
  {
    path: 'dashboard',
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: 'inspection',
        element: <InspectionPage />,
      },
      {
        path: 'vehicle',
        element: <VehiclePage />,
      },
      {
        path: 'telemetry',
        element: <TelemetryPage />,
      },
      {
        path: 'defects',
        element: <DefectsPage />,
      },
      {
        path: 'history',
        element: <HistoryPage />,
      },
      {
        path: 'reports',
        element: <ReportsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

