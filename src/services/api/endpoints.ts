/**
 * Proposed FastAPI Backend Endpoint Contracts
 * Note: These contracts define the target endpoints for Stage 5 integration.
 */

export const API_ENDPOINTS = {
  HEALTH: '/health',
  SYSTEM_STATUS: '/status',

  INSPECTIONS: {
    LIST: '/inspections',
    GET: (id: string) => `/inspections/${id}`,
    CREATE: '/inspections',
    START: (id: string) => `/inspections/${id}/start`,
    PAUSE: (id: string) => `/inspections/${id}/pause`,
    STOP: (id: string) => `/inspections/${id}/stop`,
  },

  TELEMETRY: {
    LATEST: '/telemetry/latest',
    STREAM_WS: '/ws/telemetry',
    LOG: (inspectionId: string) => `/telemetry/inspection/${inspectionId}`,
  },

  DEFECTS: {
    LIST: '/defects',
    GET: (id: string) => `/defects/${id}`,
    BY_INSPECTION: (inspectionId: string) => `/defects/inspection/${inspectionId}`,
    UPDATE_STATUS: (id: string) => `/defects/${id}/review`,
  },

  REPORTS: {
    LIST: '/reports',
    GET: (id: string) => `/reports/${id}`,
    GENERATE: '/reports/generate',
    EXPORT_PDF: (id: string) => `/reports/${id}/export.pdf`,
  },

  HARDWARE: {
    STATUS: '/hardware/status',
    CONFIG: '/hardware/config',
    CALIBRATE: '/hardware/calibrate',
  },
} as const;

