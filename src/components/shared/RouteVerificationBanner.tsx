import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { ROUTES } from '@/constants/routes';
import { SYSTEM_INFO } from '@/constants/system';
import {
  Compass,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
} from 'lucide-react';

export interface RouteVerificationBannerProps {
  routeName: string;
  routePath: string;
  targetStage: string;
  plannedFeatures: string[];
}

export const RouteVerificationBanner: FC<RouteVerificationBannerProps> = ({
  routeName,
  routePath,
  targetStage,
  plannedFeatures,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Banner Status */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-white border border-industrial-200 rounded-sm shadow-industrial-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-white rounded-sm">
            <Compass className="w-5 h-5 text-brand-orange" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs uppercase text-industrial-500">Route Verification</span>
              <Badge variant="brand" isMono>{routePath}</Badge>
            </div>
            <h2 className="text-lg font-bold text-industrial-900">{routeName}</h2>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <StatusIndicator status="healthy" label="Router Active" showPing />
          <Badge variant="default" isMono>{targetStage}</Badge>
        </div>
      </div>

      {/* Bento-grid of Route Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Stage Status */}
        <Card variant="default">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-industrial-700" />
              <CardTitle>Architecture Status</CardTitle>
            </div>
            <CardDescription>Frontend stage boundary control</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-industrial-600">Current Phase</span>
              <span className="font-mono font-medium text-industrial-900">Stage 1 Foundation</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-industrial-600">Implementation Target</span>
              <span className="font-mono font-medium text-brand-orange">{targetStage}</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-industrial-600">Route Resolution</span>
              <span className="font-mono text-status-healthy font-semibold">VERIFIED</span>
            </div>
            <p className="text-xs text-industrial-500 pt-2 border-t border-industrial-100">
              This route placeholder confirms the React Router hierarchy and design system tokens are functioning.
            </p>
          </CardContent>
        </Card>

        {/* Hardware & System Target */}
        <Card variant="default">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-brand-orange" />
              <CardTitle>System Hardware Target</CardTitle>
            </div>
            <CardDescription>Prepared for future telemetry & control</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-industrial-100">
              <span className="text-industrial-600">Controller</span>
              <span className="font-mono text-industrial-900">{SYSTEM_INFO.SPECIFICATION.CONTROLLER}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-industrial-100">
              <span className="text-industrial-600">Vision System</span>
              <span className="font-mono text-industrial-900">{SYSTEM_INFO.SPECIFICATION.CAMERA}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-industrial-100">
              <span className="text-industrial-600">AI Model</span>
              <span className="font-mono text-industrial-900">{SYSTEM_INFO.SPECIFICATION.INFERENCE_ENGINE}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-industrial-600">Odometry</span>
              <span className="font-mono text-industrial-900">{SYSTEM_INFO.SPECIFICATION.POSITIONING}</span>
            </div>
          </CardContent>
        </Card>

        {/* Planned Features for Route */}
        <Card variant="default">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-status-healthy" />
              <CardTitle>Planned Route Capabilities</CardTitle>
            </div>
            <CardDescription>Scheduled for subsequent prompts</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-xs">
              {plannedFeatures.map((feat, idx) => (
                <li key={idx} className="flex items-start gap-2 text-industrial-700">
                  <div className="w-1.5 h-1.5 rounded-none bg-brand-orange mt-1.5 shrink-0" />
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Quick Route Verification Navigation */}
      <Card variant="default">
        <CardHeader>
          <CardTitle>Route Switcher Verification Matrix</CardTitle>
          <CardDescription>
            Click any route below to verify client-side navigation without full page reload.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <NavLink
              to={ROUTES.HOME}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/ (Landing)</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.ROOT}
              end
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/dashboard</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.INSPECTION}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/inspection</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.VEHICLE}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/vehicle</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.TELEMETRY}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/telemetry</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.DEFECTS}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/defects</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.HISTORY}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/history</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.REPORTS}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/reports</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
            <NavLink
              to={ROUTES.DASHBOARD.SETTINGS}
              className={({ isActive }) =>
                `flex items-center justify-between p-2.5 text-xs font-mono border rounded-sm transition-colors ${
                  isActive
                    ? 'bg-industrial-900 text-white border-industrial-900'
                    : 'bg-industrial-50 text-industrial-700 border-industrial-200 hover:bg-industrial-100'
                }`
              }
            >
              <span>/settings</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60" />
            </NavLink>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
