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
import {
  AlertOctagon,
  Search,
  RotateCcw,
  Inbox,
  FilterX,
} from 'lucide-react';

export const DefectsPage: FC = () => {
  useDocumentTitle('Defect Registry');
  const { isDemoMode } = useAppMode();
  const { defects } = useDefects();

  const [selectedClass, setSelectedClass] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const defectClassOptions = [
    { label: 'All Defect Classes', value: 'all' },
    { label: 'Deformation', value: 'deformation' },
    { label: 'Misalignment', value: 'misalignment' },
    { label: 'Obstacle', value: 'obstacle' },
    { label: 'Rupture', value: 'rupture' },
  ];

  const reviewStatusOptions = [
    { label: 'All Review States', value: 'all' },
    { label: 'Unreviewed', value: 'unreviewed' },
    { label: 'Verified', value: 'verified' },
    { label: 'Dismissed', value: 'dismissed' },
  ];

  const handleResetFilters = () => {
    setSelectedClass('all');
    setSelectedStatus('all');
    setSearchQuery('');
  };

  // Filter pipeline executing dynamically against active dataset
  const filteredDefects = useMemo(() => {
    return defects.filter((item) => {
      // 1. Class filter
      if (selectedClass !== 'all' && item.defectClass !== selectedClass) {
        return false;
      }
      // 2. Review status filter
      if (selectedStatus !== 'all' && item.reviewStatus !== selectedStatus) {
        return false;
      }
      // 3. Search query matching ID, frameId, or notes
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase().trim();
        const matchesId = item.id.toLowerCase().includes(query);
        const matchesFrame = item.frameId.toLowerCase().includes(query);
        const matchesInspection = item.inspectionId.toLowerCase().includes(query);
        const matchesNotes = item.notes?.toLowerCase().includes(query) ?? false;

        if (!matchesId && !matchesFrame && !matchesInspection && !matchesNotes) {
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
              Trained classes: Deformation, Misalignment, Obstacle, Rupture. Defect coordinates and bounding snapshots will appear here upon detection.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 flex-wrap">
          <Badge variant="outline" isMono className="bg-white text-[10px]">Deformation</Badge>
          <Badge variant="outline" isMono className="bg-white text-[10px]">Misalignment</Badge>
          <Badge variant="outline" isMono className="bg-white text-[10px]">Obstacle</Badge>
          <Badge variant="outline" isMono className="bg-white text-[10px]">Rupture</Badge>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card variant="default" className="border-industrial-200">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
            <div className="sm:col-span-5">
              <Input
                label="Search Defect, Frame, or Inspection ID"
                placeholder="e.g. DEF-001, FRM-01420, or INS-2026..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftAddon={<Search className="w-4 h-4 text-industrial-400" />}
              />
            </div>

            <div className="sm:col-span-3">
              <Select
                label="Defect Class"
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                options={defectClassOptions}
              />
            </div>

            <div className="sm:col-span-3">
              <Select
                label="Review Status"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                options={reviewStatusOptions}
              />
            </div>

            <div className="sm:col-span-1">
              <Button
                variant={hasActiveFilters ? 'secondary' : 'outline'}
                size="md"
                onClick={handleResetFilters}
                className="w-full"
                title="Reset active filters"
                disabled={!hasActiveFilters}
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Defect Table & Empty State */}
      <Card variant="raised" className="border-industrial-300 overflow-hidden">
        <CardHeader className="p-4 pb-3 border-b border-industrial-200 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-xs uppercase font-mono tracking-wider">
              Conduit Defect Log
            </CardTitle>
            <CardDescription className="text-xs">
              Spatial catalog of all verified and flagged anomalies
            </CardDescription>
          </div>
          <Badge variant={isDemoMode ? 'brand' : 'default'} isMono className="text-[10px]">
            {filteredDefects.length} Records {isDemoMode ? '(Demo)' : ''}
          </Badge>
        </CardHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[12%]">Defect ID</TableHead>
              <TableHead className="w-[16%]">Classification</TableHead>
              <TableHead className="w-[14%]">Confidence</TableHead>
              <TableHead className="w-[14%]">Frame ID</TableHead>
              <TableHead className="w-[20%]">Capture Time (UTC)</TableHead>
              <TableHead className="w-[12%]">Distance</TableHead>
              <TableHead className="w-[12%]">Review Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredDefects.length > 0 ? (
              filteredDefects.map((defect) => (
                <TableRow key={defect.id} className="font-mono text-xs">
                  <TableCell className="font-bold text-industrial-900">
                    <div className="flex items-center gap-1.5">
                      {defect.isDemo && (
                        <span className="w-1.5 h-1.5 rounded-full bg-brand-orange" title="Demo Record" />
                      )}
                      <span>{defect.id}</span>
                    </div>
                  </TableCell>
                  <TableCell className="uppercase font-semibold text-brand-orange">
                    {defect.defectClass}
                  </TableCell>
                  <TableCell className="text-industrial-700">
                    {defect.confidence ? `${(defect.confidence * 100).toFixed(1)}%` : '--'}
                  </TableCell>
                  <TableCell className="text-industrial-600">
                    {defect.frameId}
                  </TableCell>
                  <TableCell className="text-industrial-500 text-[11px]">
                    {defect.captureTimestamp}
                  </TableCell>
                  <TableCell className="font-bold text-industrial-900">
                    {defect.estimatedDistanceMeters !== null
                      ? `${defect.estimatedDistanceMeters.toFixed(2)} m`
                      : '--'}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={defect.reviewStatus === 'verified' ? 'healthy' : 'outline'}
                      isMono
                      className="text-[10px]"
                    >
                      {defect.reviewStatus}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="p-0">
                  {isDemoMode && hasActiveFilters ? (
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
    </div>
  );
};

export default DefectsPage;
