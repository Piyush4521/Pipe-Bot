import { useState, useEffect, type FC, type ChangeEvent } from 'react';
import { cameraService, type CameraStatusPayload } from '@/services/camera/cameraService';
import { useToast } from '@/components/ui/Toast';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import {
  Camera,
  Play,
  Square,
  Upload,
} from 'lucide-react';

interface CameraStreamControlsProps {
  onFrameProcessed?: () => void;
}

export const CameraStreamControls: FC<CameraStreamControlsProps> = ({
  onFrameProcessed,
}) => {
  const { showToast } = useToast();
  const [streamUrl, setStreamUrl] = useState('http://192.168.4.1/stream');
  const [status, setStatus] = useState<CameraStatusPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const pollStatus = async () => {
    try {
      const res = await cameraService.fetchBackendStatus();
      setStatus(res);
    } catch {
      // Backend not running or offline
    }
  };

  useEffect(() => {
    pollStatus();
    const interval = setInterval(pollStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await cameraService.startStream(streamUrl.trim());
      setStatus(res);
      showToast('Camera worker started.', 'success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to start camera worker.';
      showToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    try {
      const res = await cameraService.stopStream();
      setStatus(res);
      showToast('Camera worker stopped.', 'info');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to stop camera worker.';
      showToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const res = await cameraService.ingestFrame(file, 1);
      showToast(
        res.defectDetected
          ? `Frame processed: ${res.detectionsCount} defect(s) detected!`
          : 'Frame processed: No defects detected in frame.',
        res.defectDetected ? 'error' : 'success'
      );
      onFrameProcessed?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Frame upload failed.';
      showToast(msg, 'error');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const isConnected = status?.state === 'connected';

  return (
    <Card variant="raised" className="border-industrial-300">
      <CardHeader className="p-4 pb-3 border-b border-industrial-200 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-brand-orange" />
          <CardTitle className="text-xs font-mono uppercase tracking-wider">
            Camera Worker & Ingestion Controls
          </CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <StatusIndicator
            status={isConnected ? 'healthy' : 'offline'}
            label={status?.state ? `State: ${status.state}` : 'State: Disconnected'}
            size="sm"
          />
          <Badge variant="outline" isMono className="text-[10px]">
            {status?.currentFps ? `${status.currentFps.toFixed(1)} FPS` : '0.0 FPS'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {/* Stream URL configuration */}
        <div className="space-y-1.5">
          <label className="block text-xs font-mono font-semibold text-industrial-800">
            ESP32-CAM MJPEG Endpoint URL
          </label>
          <div className="flex gap-2">
            <Input
              value={streamUrl}
              onChange={(e) => setStreamUrl(e.target.value)}
              placeholder="http://192.168.4.1/stream"
              className="text-xs font-mono flex-1"
            />
            {!isConnected ? (
              <Button
                variant="primary"
                size="sm"
                onClick={handleStart}
                disabled={isLoading}
                leftIcon={<Play className="w-3.5 h-3.5" />}
              >
                Connect
              </Button>
            ) : (
              <Button
                variant="danger"
                size="sm"
                onClick={handleStop}
                disabled={isLoading}
                leftIcon={<Square className="w-3.5 h-3.5" />}
              >
                Stop
              </Button>
            )}
          </div>
        </div>

        {/* Worker Telemetry Metrics */}
        <div className="grid grid-cols-3 gap-2 text-xs font-mono bg-industrial-50 p-2.5 rounded-sm border border-industrial-200">
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Frames Ingested</span>
            <span className="font-bold text-industrial-900">{status?.framesIngested ?? 0}</span>
          </div>
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Frames Decoded</span>
            <span className="font-bold text-status-healthy">{status?.framesDecoded ?? 0}</span>
          </div>
          <div>
            <span className="text-industrial-500 block text-[10px] uppercase">Frames Dropped</span>
            <span className="font-bold text-status-critical">{status?.framesDropped ?? 0}</span>
          </div>
        </div>

        {/* Single Frame Ingestion Tool */}
        <div className="pt-2 border-t border-industrial-200 flex items-center justify-between">
          <div className="text-xs text-industrial-600 font-mono">
            <span>Test Inference on Optical Frame</span>
          </div>
          <label className="cursor-pointer">
            <input
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={isUploading}
              leftIcon={<Upload className="w-3.5 h-3.5" />}
              className="text-xs"
              onClick={(e) => {
                const input = (e.currentTarget.previousElementSibling as HTMLInputElement);
                input?.click();
              }}
            >
              {isUploading ? 'Evaluating...' : 'Upload Frame (JPG)'}
            </Button>
          </label>
        </div>
      </CardContent>
    </Card>
  );
};
