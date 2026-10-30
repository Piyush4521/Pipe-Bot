import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useAppContext } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  FileText,
  Download,
  Inbox,
} from 'lucide-react';

export const ReportsPage: FC = () => {
  useDocumentTitle('Inspection Reports');
  const { isDemoMode } = useAppMode();
  const { reports } = useAppContext();

  return (
    <div className="space-y-6">
      {/* Information Header Banner */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-mono font-bold uppercase text-industrial-900">
                Inspection Compliance & Engineering Reports
              </h2>
              {isDemoMode && (
                <Badge variant="brand" isMono className="text-[10px]">
                  DEMO DATA
                </Badge>
              )}
            </div>
            <p className="text-xs text-industrial-600 mt-0.5">
              Automated compilation of pipeline condition grades, anomaly photos, and odometry metrics for municipal sign-off.
            </p>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          disabled
          leftIcon={<Download className="w-3.5 h-3.5" />}
          title="Reports will be available after inspection records are generated"
        >
          Export Batch Summary
        </Button>
      </div>

      {/* Reports Table Container */}
      <Card variant="raised" className="border-industrial-300 overflow-hidden">
        <CardHeader className="p-4 pb-3 border-b border-industrial-200 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-xs uppercase font-mono tracking-wider">
              Generated Engineering Reports
            </CardTitle>
            <CardDescription className="text-xs">
              Structured inspection documents indexed by mission run
            </CardDescription>
          </div>
          <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
            {reports.length} Reports {isDemoMode ? '(Demo)' : ''}
          </Badge>
        </CardHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[18%]">Report ID</TableHead>
              <TableHead className="w-[18%]">Inspection ID</TableHead>
              <TableHead className="w-[20%]">Generation Date</TableHead>
              <TableHead className="w-[14%]">Defects Logged</TableHead>
              <TableHead className="w-[14%]">Condition Grade</TableHead>
              <TableHead className="w-[16%]">Document Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.length > 0 ? (
              reports.map((report) => (
                <TableRow key={report.id} className="font-mono text-xs">
                  <TableCell className="font-bold text-industrial-900">
                    <div className="flex items-center gap-1.5">
                      {isDemoMode && <span className="w-1.5 h-1.5 rounded-full bg-brand-orange" />}
                      <span>{report.reportId}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-industrial-700">
                    {report.inspectionId}
                  </TableCell>
                  <TableCell className="text-industrial-600">
                    {report.generatedAt}
                  </TableCell>
                  <TableCell className="text-brand-orange font-bold">
                    {report.defectCount}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" isMono className="text-[10px]">
                      Grade {report.overallRating}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" disabled leftIcon={<Download className="w-3.5 h-3.5" />}>
                      PDF Export (Locked)
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="p-0">
                  <EmptyState
                    icon={<Inbox className="w-8 h-8 text-industrial-400" />}
                    title="Reports will be available after inspection records are generated."
                    description="When a physical or simulated conduit inspection run concludes, automated PDF summary documents and tabular data exports will compile here."
                    action={
                      <NavLink to={ROUTES.DASHBOARD.INSPECTION}>
                        <Button variant="outline" size="sm">
                          Go to Live Inspection
                        </Button>
                      </NavLink>
                    }
                  />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
};

export default ReportsPage;
