import { APP_CONFIG } from '@/constants/config';
import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { ConnectionState } from '@/types';

export interface CameraStatusPayload {
  state: ConnectionState;
  streamUrl?: string | null;
  framesIngested?: number;
  framesDecoded?: number;
  framesDropped?: number;
  currentFps?: number;
  lastFrameTimestamp?: string | null;
  cameraLatencyMs?: number | null;
  resolution?: string;
  bytesReceived?: number;
}

export class CameraService {
  private status: ConnectionState = 'disconnected';
  private defaultUrl: string;

  constructor(defaultUrl: string = APP_CONFIG.cameraStreamUrl) {
    this.defaultUrl = defaultUrl;
  }

  public getStatus(): ConnectionState {
    if (!this.defaultUrl) {
      return 'disconnected';
    }
    return this.status;
  }

  public getStreamUrl(): string {
    return this.defaultUrl;
  }

  public setStreamUrl(url: string): void {
    this.defaultUrl = url;
    if (!url) {
      this.status = 'disconnected';
    }
  }

  /**
   * Fetch optical camera status from the backend service.
   */
  public async fetchBackendStatus(): Promise<CameraStatusPayload> {
    return apiClient<CameraStatusPayload>(API_ENDPOINTS.CAMERA.STATUS);
  }

  /**
   * Start camera worker stream ingestion on the backend.
   */
  public async startStream(streamUrl?: string): Promise<CameraStatusPayload> {
    const url = streamUrl || this.defaultUrl || undefined;
    return apiClient<CameraStatusPayload>(API_ENDPOINTS.CAMERA.START, {
      method: 'POST',
      params: url ? { stream_url: url } : undefined,
    });
  }

  /**
   * Stop camera worker stream ingestion on the backend.
   */
  public async stopStream(): Promise<CameraStatusPayload> {
    return apiClient<CameraStatusPayload>(API_ENDPOINTS.CAMERA.STOP, {
      method: 'POST',
    });
  }

  /**
   * Ingest a single frame image file for inference.
   */
  public async ingestFrame(
    file: File,
    inspectionId: number = 1
  ): Promise<{ status: string; defectDetected: boolean; detectionsCount: number }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('inspection_id', String(inspectionId));

    const response = await fetch(`${APP_CONFIG.apiBaseUrl}${API_ENDPOINTS.CAMERA.FRAME}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Frame ingestion failed: ${response.status} ${text}`);
    }

    return response.json();
  }

  /**
   * Probes whether the optical stream endpoint responds (e.g. image ping).
   * Does NOT simulate video if unreachable.
   */
  public async probeStreamAvailability(timeoutMs = 2500): Promise<boolean> {
    if (!this.defaultUrl) {
      this.status = 'disconnected';
      return false;
    }

    this.status = 'connecting';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      await fetch(this.defaultUrl, {
        method: 'HEAD',
        mode: 'no-cors',
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      this.status = 'connected';
      return true;
    } catch {
      clearTimeout(timeoutId);
      this.status = 'error';
      return false;
    }
  }
}

export const cameraService = new CameraService();
