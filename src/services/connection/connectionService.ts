import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { SystemConnectionStatus } from '@/types';

export const connectionService = {
  async checkBackendHealth(): Promise<{ status: string; version: string }> {
    return apiClient<{ status: string; version: string }>(API_ENDPOINTS.HEALTH, {
      timeoutMs: 3000,
    });
  },

  async getSystemStatus(): Promise<SystemConnectionStatus> {
    return apiClient<SystemConnectionStatus>(API_ENDPOINTS.SYSTEM_STATUS, {
      timeoutMs: 3000,
    });
  },
};

