import { useState, useMemo, type FC } from 'react';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useAppMode, useDefects } from '@/app/providers/AppContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { EmptyState } from '@/components/ui/EmptyState';
import { DefectDetailDrawer } from '@/components/defects/DefectDetailDrawer';
import type { DefectDetection } from '@/types';
import {
  AlertOctagon,
  Search,
  RotateCcw,
  Inbox,
  FilterX,
  ExternalLink,
} from 'lucide-react';

export const DefectsPage: FC = () => {
  useDocumentTitle('Defect Registry');
  const { isDemoMode } = useAppMode();
  const { defects, updateDefectStatus } = useDefects();

  const [selectedClass, setSelectedClass] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeDefect, setActiveDefect] = useState<DefectDetection | null>(null);

  const defectClassOptions = [
    { label: 'All Defect Classes', value: 'all' },
    { label: 'Deformation', value: 'deformation' },
    { label: 'Misalignment', value: 'misalignment' },
    { label: 'Obstacle', value: 'obstacle' },
    { label: 'Rupture', value: 'rupture' },
  ];

  const reviewStatusOptions = [
    { label: 'All Review States', value: 'all' },
    { label: 'Unreviewed / Pending', value: 'unreviewed' },
    { label: 'Verified / Confirmed', value: 'verified' },
    { label: 'Dismissed / Rejected', value: 'dismissed' },
  ];

  const handleResetFilters = () => {
    setSelectedClass('all');
    setSelectedStatus('all');
    setSearchQuery('');
  };

  // Filter pipeline executing dynamically against active dataset
  const filteredDefects = useMemo(() => {
    return defects.filter((item) => {
      // 1. Class filter (case-insensitive)
      if (selectedClass !== 'all') {
        if (item.defectClass.toLowerCase() !== selectedClass.toLowerCase()) {
          return false;
        }
      }

      // 2. Review status filter (handling status aliases)
      if (selectedStatus !== 'all') {
        const itemStatus = (item.reviewStatus || '').toLowerCase();
        if (selectedStatus === 'unreviewed' && itemStatus !== 'unreviewed' && itemStatus !== 'pending') {
          return false;
        }
        if (selectedStatus === 'verified' && itemStatus !== 'verified' && itemStatus !== 'confirmed') {
          return false;
        }
        if (selectedStatus === 'dismissed' && itemStatus !== 'dismissed' && itemStatus !== 'rejected') {
          return false;
        }
      }

      // 3. Search query matching ID, frameId, or notes
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase().trim();
        const matchesId = String(item.id || '').toLowerCase().includes(query);
        const matchesDefectId = item.defectId ? item.defectId.toLowerCase().includes(query) : false;
        const matchesFrame = (item.frameId || '').toLowerCase().includes(query);
        const matchesInspection = String(item.inspectionId || '').toLowerCase().includes(query);
        const matchesNotes = item.notes?.toLowerCase().includes(query) ?? false;

        if (!matchesId && !matchesDefectId && !matchesFrame && !matchesInspection && !matchesNotes) {
          return false;
        }
      }

      return true;
    });
  }, [defects, selectedClass, selectedStatus, searchQuery]);

  const hasActiveFilters = selectedClass !== 'all' || selectedStatus !== 'all' || searchQuery.trim() !== '';

  return (
    <div className="space-y-6">
      {/* Target Defect Classes Header Pill */}
      <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-industrial-900 text-brand-orange rounded-sm shrink-0">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-mono font-bold uppercase text-industrial-900">
                YOLO Target Anomaly Registry
              </h2>
              {isDemoMode && (
                <Badge variant="brand" isMono className="text-[10px]">
                  DEMO DATASET ACTIVE
                </Badge>
              )}
            </div>
            <p className="text-xs text-industrial-600 mt-0.5">
              Trained classes: Deformation, Misalignment, Obstacle, Rupture. Defect coordinates and bounding snapshots will appear here upon detection. Click any row to inspect optical evidence.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <Badge variant="outline" isMono className="text-[10px]">
            Total Logged: {defects.length}
          </Badge>
          <Badge variant="brand" isMono className="text-[10px]">
            Filtered: {filteredDefects.length}
          </Badge>
        </div>
      </div>

      {/* Filter and Query Toolbar */}
      <Card variant="default" className="border-industrial-200">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
            {/* Search Input */}
            <div className="sm:col-span-5 relative">
              <Search className="w-4 h-4 text-industrial-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by Defect ID, Frame, or note..."
                className="pl-9 text-xs"
              />
            </div>

            {/* Class Filter Dropdown */}
            <div className="sm:col-span-3">
              <Select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                options={defectClassOptions}
                className="text-xs"
              />
            </div>

            {/* Review Status Dropdown */}
            <div className="sm:col-span-3">
              <Select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                options={reviewStatusOptions}
                className="text-xs"
              />
            </div>

            {/* Reset Filters Button */}
            <div className="sm:col-span-1 flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetFilters}
                disabled={!hasActiveFilters}
                title="Reset all search queries and dropdown filters"
                className="w-full sm:w-auto p-2"
                aria-label="Reset filters"
              >
                <RotateCcw className="w-4 h-4 text-industrial-600" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Defects Table View */}
      <Card variant="raised" className="border-industrial-300 overflow-hidden">
        <CardHeader className="p-4 pb-3 border-b border-industrial-200 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-xs uppercase font-mono tracking-wider">
              Anomalies & Defect Detections
            </CardTitle>
            <CardDescription className="text-xs">
              Correlated frame detections with spatial odometry and verification audit states
            </CardDescription>
          </div>
          <span className="text-[11px] font-mono text-industrial-500">
            Click row for verification controls
          </span>
        </CardHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[14%]">Defect ID</TableHead>
              <TableHead className="w-[16%]">Classification</TableHead>
              <TableHead className="w-[14%]">Confidence</TableHead>
              <TableHead className="w-[14%]">Frame ID</TableHead>
              <TableHead className="w-[18%]">Capture Time (UTC)</TableHead>
              <TableHead className="w-[12%]">Distance</TableHead>
              <TableHead className="w-[12%]">Review Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredDefects.length > 0 ? (
              filteredDefects.map((defect) => {
                const isConfirmed =
                  defect.reviewStatus === 'confirmed' || defect.reviewStatus === 'verified';
                const isRejected =
                  defect.reviewStatus === 'rejected' || defect.reviewStatus === 'dismissed';

                return (
                  <TableRow
                    key={defect.id}
                    onClick={() => setActiveDefect(defect)}
                    className="font-mono text-xs cursor-pointer hover:bg-industrial-100 transition-colors"
                  >
                    <TableCell className="font-bold text-industrial-900">
                      <div className="flex items-center gap-1.5">
                        {defect.isDemo && (
                          <span className="w-1.5 h-1.5 rounded-full bg-brand-orange" title="Demo Record" />
                        )}
                        <span>{defect.defectId || defect.id}</span>
                        <ExternalLink className="w-3 h-3 text-industrial-400 opacity-0 group-hover:opacity-100" />
                      </div>
                    </TableCell>
                    <TableCell className="uppercase font-semibold text-brand-orange">
                      {defect.defectClass}
                    </TableCell>
                    <TableCell className="text-industrial-700">
                      {defect.confidence != null ? `${(defect.confidence * 100).toFixed(1)}%` : '--'}
                    </TableCell>
                    <TableCell className="text-industrial-600">
                      {defect.frameId}
                    </TableCell>
                    <TableCell className="text-industrial-500 text-[11px]">
                      {defect.captureTimestamp ? new Date(defect.captureTimestamp).toLocaleTimeString() : '--'}
                    </TableCell>
                    <TableCell className="font-bold text-industrial-900">
                      {defect.estimatedDistanceMeters !== null && defect.estimatedDistanceMeters !== undefined
                        ? `${defect.estimatedDistanceMeters.toFixed(2)} m`
                        : '--'}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={isConfirmed ? 'healthy' : isRejected ? 'critical' : 'outline'}
                        isMono
                        className="text-[10px] uppercase"
                      >
                        {defect.reviewStatus}
                      </Badge>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="p-0">
                  {hasActiveFilters ? (
                    <EmptyState
                      icon={<FilterX className="w-8 h-8 text-industrial-400" />}
                      title="No matching defects found"
                      description="No records match your selected filter criteria. Try adjusting your query or resetting the filter toolbar."
                      action={
                        <Button variant="outline" size="sm" onClick={handleResetFilters} leftIcon={<RotateCcw className="w-3.5 h-3.5" />}>
                          Reset Filters
                        </Button>
                      }
                    />
                  ) : (
                    <EmptyState
                      icon={<Inbox className="w-8 h-8 text-industrial-400" />}
                      title="No defects detected or logged yet."
                      description="When an inspection run is active, the YOLO vision head evaluates frames and logs classified structural defects here."
                    />
                  )}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Defect Detail & Evidence Review Drawer */}
      <DefectDetailDrawer
        defect={activeDefect}
        onClose={() => setActiveDefect(null)}
        onUpdateStatus={updateDefectStatus}
      />
    </div>
  );
};

export default DefectsPage;
