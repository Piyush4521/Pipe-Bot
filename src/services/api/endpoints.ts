/**
 * Proposed FastAPI Backend Endpoint Contracts
 * Note: These contracts define the target endpoints for Stage 5 integration.
 */

export const API_ENDPOINTS = {
  HEALTH: '/health',
  SYSTEM_STATUS: '/system/status',
  STATUS_ALIAS: '/status',

  INSPECTIONS: {
    LIST: '/inspections',
    GET: (id: string | number) => `/inspections/${id}`,
    CREATE: '/inspections',
    START: (id: string | number) => `/inspections/${id}/start`,
    PAUSE: (id: string | number) => `/inspections/${id}/pause`,
    STOP: (id: string | number) => `/inspections/${id}/stop`,
  },

  TELEMETRY: {
    LATEST: '/telemetry/latest',
    STREAM_WS: '/ws/telemetry',
    LOG: (inspectionId: string | number) => `/telemetry/inspection/${inspectionId}`,
  },

  DEFECTS: {
    LIST: '/defects',
    GET: (id: string | number) => `/defects/${id}`,
    BY_INSPECTION: (inspectionId: string | number) => `/defects/inspection/${inspectionId}`,
    UPDATE_STATUS: (id: string | number) => `/defects/${id}/review`,
  },

  CAMERA: {
    STATUS: '/camera/status',
    START: '/camera/start',
    STOP: '/camera/stop',
    FRAME: '/camera/frame',
  },

  VISION: {
    STATUS: '/vision/status',
    MODELS: '/vision/models',
  },

  MEDIA: {
    RETRIEVE: (uuid: string) => `/media/${uuid}`,
  },

  REPORTS: {
    LIST: '/reports',
    GET: (id: string | number) => `/reports/${id}`,
    GENERATE: '/reports/generate',
    EXPORT_PDF: (id: string | number) => `/reports/${id}/export.pdf`,
  },

  HARDWARE: {
    STATUS: '/hardware/status',
    CONFIG: '/hardware/config',
    CALIBRATE: '/hardware/calibrate',
  },
} as const;
