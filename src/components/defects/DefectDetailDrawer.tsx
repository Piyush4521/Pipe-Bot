import { useState, type FC } from 'react';
import type { DefectDetection, DefectReviewStatus } from '@/types';
import { useToast } from '@/components/ui/Toast';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  X,
  CheckCircle,
  XCircle,
  Clock,
  Camera,
  AlertOctagon,
} from 'lucide-react';

interface DefectDetailDrawerProps {
  defect: DefectDetection | null;
  onClose: () => void;
  onUpdateStatus: (id: string | number, status: DefectReviewStatus, notes?: string) => Promise<void>;
}

export const DefectDetailDrawer: FC<DefectDetailDrawerProps> = ({
  defect,
  onClose,
  onUpdateStatus,
}) => {
  const { showToast } = useToast();
  const [reviewNotes, setReviewNotes] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  if (!defect) return null;

  const handleStatusChange = async (newStatus: DefectReviewStatus) => {
    setIsUpdating(true);
    try {
      await onUpdateStatus(defect.id, newStatus, reviewNotes.trim() || undefined);
      showToast(`Defect marked as ${newStatus}.`, 'success');
      onClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to update review status.';
      showToast(msg, 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="drawer-title"
      className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l-2 border-industrial-900 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200"
    >
      {/* Drawer Header */}
      <div className="p-4 bg-industrial-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-brand-orange" />
          <h2 id="drawer-title" className="text-xs font-mono font-bold uppercase tracking-wider">
            Defect Evidence Review
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-industrial-400 hover:text-white p-1 rounded-sm focus:outline-none"
          aria-label="Close defect details"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Identity & Status */}
        <div className="flex items-center justify-between pb-3 border-b border-industrial-200">
          <div>
            <div className="text-[11px] font-mono text-industrial-500 uppercase">Defect Public Tag</div>
            <div className="text-base font-bold font-mono text-industrial-950">{defect.defectId || defect.id}</div>
          </div>
          <Badge variant="brand" isMono className="text-xs font-bold uppercase">
            {defect.defectClass}
          </Badge>
        </div>

        {/* Optical Frame Snapshot Preview */}
        <div className="space-y-1.5">
          <div className="text-xs font-mono font-semibold text-industrial-800 flex items-center gap-1.5">
            <Camera className="w-3.5 h-3.5 text-industrial-600" />
            <span>Optical Evidence Capture</span>
          </div>
          <div className="aspect-video bg-industrial-900 rounded-sm border border-industrial-800 flex flex-col items-center justify-center p-4 text-center select-none">
            {defect.snapshotUrl ? (
              <img
                src={defect.snapshotUrl}
                alt={`Evidence of ${defect.defectClass}`}
                className="max-h-full max-w-full object-contain"
              />
            ) : (
              <div className="text-industrial-500 space-y-1 font-mono text-xs">
                <Camera className="w-8 h-8 mx-auto text-industrial-600" />
                <div className="text-[11px]">Frame: {defect.frameId}</div>
                <div className="text-[10px] text-industrial-600">Snapshot URI: stored in backend archive</div>
              </div>
            )}
          </div>
        </div>

        {/* Diagnostic Metadata Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs font-mono bg-industrial-50 p-3 rounded-sm border border-industrial-200">
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Confidence</span>
            <span className="font-bold text-industrial-900">
              {defect.confidence != null ? `${(defect.confidence * 100).toFixed(1)}%` : '--'}
            </span>
          </div>
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Odometry Position</span>
            <span className="font-bold text-brand-orange">
              {defect.estimatedDistanceMeters != null ? `${defect.estimatedDistanceMeters.toFixed(2)} m` : '--'}
            </span>
          </div>
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Optical Capture UTC</span>
            <span className="text-industrial-800 text-[11px] truncate block">
              {defect.captureTimestamp ? new Date(defect.captureTimestamp).toLocaleTimeString() : '--'}
            </span>
          </div>
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Current Review State</span>
            <span className="font-bold uppercase text-industrial-900">{defect.reviewStatus}</span>
          </div>
        </div>

        {/* Existing Notes */}
        {defect.notes && (
          <div className="p-3 bg-industrial-100 rounded-sm border border-industrial-300 text-xs">
            <span className="font-mono font-bold text-industrial-700 block text-[10px] uppercase mb-1">
              Field & Audit Notes:
            </span>
            <p className="text-industrial-800 whitespace-pre-wrap">{defect.notes}</p>
          </div>
        )}

        {/* Operator Review Form */}
        <div className="space-y-2 pt-2 border-t border-industrial-200">
          <label className="block text-xs font-mono font-semibold text-industrial-800">
            Operator Verification Annotation
          </label>
          <textarea
            value={reviewNotes}
            onChange={(e) => setReviewNotes(e.target.value)}
            placeholder="Add engineering remarks before confirming or rejecting this detection..."
            rows={3}
            className="w-full text-xs p-2.5 bg-white border border-industrial-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-brand-orange font-sans"
          />
        </div>
      </div>

      {/* Review Actions Footer */}
      <div className="p-4 bg-industrial-100 border-t border-industrial-200 flex items-center justify-between gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleStatusChange('pending')}
          disabled={isUpdating}
          leftIcon={<Clock className="w-3.5 h-3.5" />}
          className="text-xs"
        >
          Pending
        </Button>
        <div className="flex items-center gap-2">
          <Button
            variant="danger"
            size="sm"
            onClick={() => handleStatusChange('rejected')}
            disabled={isUpdating}
            leftIcon={<XCircle className="w-3.5 h-3.5" />}
            className="text-xs"
          >
            Reject
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleStatusChange('confirmed')}
            disabled={isUpdating}
            leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
            className="text-xs"
          >
            Confirm
          </Button>
        </div>
      </div>
    </div>
  );
};
