import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useInspection } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  History,
  Play,
  PlusCircle,
  Inbox,
} from 'lucide-react';

export const HistoryPage: FC = () => {
  useDocumentTitle('Inspection History');
  const { isDemoMode } = useAppMode();
  const { inspections } = useInspection();

  return (
    <div className="space-y-6">
      {/* Top Action Header */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
            <History className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-mono font-bold uppercase text-industrial-900">
                Pipeline Inspection Mission Archive
              </h2>
              {isDemoMode && (
                <Badge variant="brand" isMono className="text-[10px]">
                  DEMO DATA
                </Badge>
              )}
            </div>
            <p className="text-xs text-industrial-600 mt-0.5">
              Historical catalog of completed and archived conduit crawl sessions with odometry distances and defect metrics.
            </p>
          </div>
        </div>

        <NavLink to={ROUTES.DASHBOARD.INSPECTION}>
          <Button variant="primary" size="sm" leftIcon={<PlusCircle className="w-3.5 h-3.5" />}>
            New Inspection Session
          </Button>
        </NavLink>
      </div>

      {/* History Table Container */}
      <Card variant="raised" className="border-industrial-300 overflow-hidden">
        <CardHeader className="p-4 pb-3 border-b border-industrial-200 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-xs uppercase font-mono tracking-wider">
              Mission Log History
            </CardTitle>
            <CardDescription className="text-xs">
              Chronological listing of archived pipeline runs
            </CardDescription>
          </div>
          <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
            {inspections.length} Sessions {isDemoMode ? '(Demo)' : ''}
          </Badge>
        </CardHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[18%]">Inspection ID</TableHead>
              <TableHead className="w-[22%]">Inspection Date</TableHead>
              <TableHead className="w-[18%]">Conduit ID</TableHead>
              <TableHead className="w-[16%]">Total Distance</TableHead>
              <TableHead className="w-[14%]">Defects Logged</TableHead>
              <TableHead className="w-[12%]">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {inspections.length > 0 ? (
              inspections.map((record) => (
                <TableRow key={record.id} className="font-mono text-xs">
                  <TableCell className="font-bold text-industrial-900">
                    <div className="flex items-center gap-1.5">
                      {isDemoMode && <span className="w-1.5 h-1.5 rounded-full bg-brand-orange" />}
                      <span>{record.inspectionId}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-industrial-600">
                    {record.startedAt}
                  </TableCell>
                  <TableCell className="text-industrial-800">
                    {record.pipeIdentifier}
                  </TableCell>
                  <TableCell className="font-bold text-industrial-900">
                    {record.totalDistanceMeters.toFixed(2)} m
                  </TableCell>
                  <TableCell className="text-brand-orange font-bold">
                    {record.defectCount}
                  </TableCell>
                  <TableCell>
                    <Badge variant="healthy" isMono className="text-[10px]">
                      {record.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="p-0">
                  <EmptyState
                    icon={<Inbox className="w-8 h-8 text-industrial-400" />}
                    title="No inspection history available."
                    description="Completed conduit inspection missions and odometry logs will be automatically recorded here."
                    action={
                      <NavLink to={ROUTES.DASHBOARD.INSPECTION}>
                        <Button variant="outline" size="sm" leftIcon={<Play className="w-3.5 h-3.5" />}>
                          Launch Live Inspection
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

export default HistoryPage;
