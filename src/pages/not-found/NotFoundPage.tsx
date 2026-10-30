import type { FC } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ROUTES } from '@/constants/routes';
import { AlertTriangle, Home, LayoutDashboard } from 'lucide-react';

export const NotFoundPage: FC = () => {
  useDocumentTitle('Page Not Found');
  const location = useLocation();

  return (
    <div className="min-h-[70vh] flex items-center justify-center py-12">
      <Card variant="raised" className="max-w-lg w-full text-center border-industrial-300">
        <CardHeader className="items-center pb-2">
          <div className="w-12 h-12 bg-industrial-100 rounded-sm flex items-center justify-center text-status-warning mb-2 border border-industrial-200">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs uppercase text-industrial-500">Error 404</span>
            <Badge variant="warning" isMono>Route Not Found</Badge>
          </div>
          <CardTitle className="text-xl mt-1">Unrecognized Pipeline Route</CardTitle>
          <CardDescription>
            The requested path does not map to any active PipeBot frontend endpoint.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6 pt-4">
          <div className="p-3 bg-industrial-100 border border-industrial-200 rounded-sm">
            <span className="text-xs text-industrial-500 font-mono">Attempted Path:</span>
            <div className="font-mono text-sm font-semibold text-industrial-900 break-all mt-0.5">
              {location.pathname}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <NavLink to={ROUTES.HOME} className="w-full sm:w-auto">
              <Button variant="secondary" size="md" className="w-full" leftIcon={<Home className="w-4 h-4" />}>
                Return to Landing
              </Button>
            </NavLink>
            <NavLink to={ROUTES.DASHBOARD.ROOT} className="w-full sm:w-auto">
              <Button variant="primary" size="md" className="w-full" leftIcon={<LayoutDashboard className="w-4 h-4" />}>
                Go to Dashboard
              </Button>
            </NavLink>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
