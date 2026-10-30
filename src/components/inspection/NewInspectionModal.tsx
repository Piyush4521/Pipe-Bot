import { useState, type FC, type FormEvent } from 'react';
import { useInspection } from '@/app/providers/AppContext';
import { useToast } from '@/components/ui/Toast';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { X, Play, AlertCircle } from 'lucide-react';

interface NewInspectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const NewInspectionModal: FC<NewInspectionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { createInspection } = useInspection();
  const { showToast } = useToast();

  const [pipeIdentifier, setPipeIdentifier] = useState('PVC-RUN-002');
  const [pipeDiameterMm, setPipeDiameterMm] = useState(200);
  const [pipeMaterial, setPipeMaterial] = useState('PVC');
  const [operatorId, setOperatorId] = useState('TECH-FIELD-01');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!pipeIdentifier.trim()) {
      setError('Please provide a conduit tag or pipe identifier.');
      return;
    }

    if (!operatorId.trim()) {
      setError('Operator ID is required for audit traceability.');
      return;
    }

    setIsSubmitting(true);
    try {
      const created = await createInspection({
        pipeIdentifier: pipeIdentifier.trim(),
        pipeDiameterMm: Number(pipeDiameterMm),
        pipeMaterial,
        operatorId: operatorId.trim(),
        notes: notes.trim() || undefined,
      });

      showToast(`Inspection ${created.inspectionId} initialized successfully!`, 'success');
      onSuccess?.();
      onClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create inspection session.';
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-industrial-950/60 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="bg-white border-2 border-industrial-900 rounded-none shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="px-5 py-3.5 bg-industrial-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-brand-orange" />
            <h2 id="modal-title" className="text-xs font-mono font-bold uppercase tracking-wider">
              Initialize New Inspection Session
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-industrial-400 hover:text-white p-1 rounded-sm focus:outline-none focus:ring-1 focus:ring-brand-orange"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-status-critical-bg border border-status-critical-border text-industrial-900 rounded-sm text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-status-critical shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="block text-xs font-mono font-semibold text-industrial-800">
              Conduit Identifier Tag <span className="text-status-critical">*</span>
            </label>
            <Input
              value={pipeIdentifier}
              onChange={(e) => setPipeIdentifier(e.target.value)}
              placeholder="e.g. PVC-MAIN-001"
              required
              className="text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="block text-xs font-mono font-semibold text-industrial-800">
                Pipe Material
              </label>
              <Select
                value={pipeMaterial}
                onChange={(e) => setPipeMaterial(e.target.value)}
                options={[
                  { label: 'PVC (Polyvinyl Chloride)', value: 'PVC' },
                  { label: 'HDPE (Polyethylene)', value: 'HDPE' },
                  { label: 'Concrete Conduit', value: 'Concrete' },
                  { label: 'Cast Iron', value: 'CastIron' },
                ]}
                className="text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-mono font-semibold text-industrial-800">
                Diameter (mm)
              </label>
              <Input
                type="number"
                min={50}
                max={1200}
                value={pipeDiameterMm}
                onChange={(e) => setPipeDiameterMm(Number(e.target.value))}
                className="text-xs font-mono"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-mono font-semibold text-industrial-800">
              Operator / Technician ID <span className="text-status-critical">*</span>
            </label>
            <Input
              value={operatorId}
              onChange={(e) => setOperatorId(e.target.value)}
              placeholder="e.g. OP-TECH-042"
              required
              className="text-xs"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-mono font-semibold text-industrial-800">
              Field Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Conduit location, weather conditions, or preliminary observations..."
              rows={3}
              className="w-full text-xs p-2.5 bg-white border border-industrial-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-brand-orange"
            />
          </div>

          <div className="pt-3 border-t border-industrial-200 flex items-center justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={isSubmitting}
              leftIcon={<Play className="w-3.5 h-3.5" />}
            >
              {isSubmitting ? 'Creating...' : 'Initialize Mission'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
