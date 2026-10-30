import { APP_CONFIG } from '@/constants/config';
import type { ConnectionState } from '@/types';

export interface CameraStreamConfig {
  streamUrl: string;
  resolution: string;
  fpsTarget: number;
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
