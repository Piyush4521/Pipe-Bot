/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_WS_URL?: string;
  readonly VITE_CAMERA_STREAM_URL?: string;
  readonly VITE_APP_MODE?: 'disconnected' | 'demo' | 'live';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
