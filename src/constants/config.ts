/**
 * Centralized Application and Environment Configuration
 * Validates Vite environment variables and provides safe local defaults.
 */

export type AppMode = 'disconnected' | 'demo' | 'live';

export interface AppConfig {
  apiBaseUrl: string;
  wsUrl: string;
  cameraStreamUrl: string;
  defaultMode: AppMode;
  apiTimeoutMs: number;
}

const metaEnv = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env : undefined;
const rawMode = metaEnv?.VITE_APP_MODE;
const validatedMode: AppMode =
  rawMode === 'demo' || rawMode === 'live' || rawMode === 'disconnected'
    ? rawMode
    : 'disconnected';

export const APP_CONFIG: AppConfig = {
  apiBaseUrl: metaEnv?.VITE_API_BASE_URL || '',
  wsUrl: metaEnv?.VITE_WS_URL || '',
  cameraStreamUrl: metaEnv?.VITE_CAMERA_STREAM_URL || '',
  defaultMode: validatedMode,
  apiTimeoutMs: 10000,
};

