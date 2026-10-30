export const ROUTES = {
  HOME: '/',
  PRIVACY: '/privacy',
  TERMS: '/terms',
  DASHBOARD: {
    ROOT: '/dashboard',
    INSPECTION: '/dashboard/inspection',
    VEHICLE: '/dashboard/vehicle',
    TELEMETRY: '/dashboard/telemetry',
    DEFECTS: '/dashboard/defects',
    HISTORY: '/dashboard/history',
    REPORTS: '/dashboard/reports',
    SETTINGS: '/dashboard/settings',
  },
} as const;

export type RouteKey = typeof ROUTES;

