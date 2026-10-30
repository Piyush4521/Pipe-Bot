import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { EncoderTelemetry, IMUTelemetry, VehicleTelemetry } from '@/types';

export interface LatestTelemetryResponse {
  encoder: EncoderTelemetry;
  imu: IMUTelemetry;
  vehicle: VehicleTelemetry;
  timestamp: string;
}

export const telemetryService = {
  async getLatestTelemetry(): Promise<LatestTelemetryResponse> {
    return apiClient<LatestTelemetryResponse>(API_ENDPOINTS.TELEMETRY.LATEST);
  },

  async getTelemetryLog(inspectionId: string): Promise<LatestTelemetryResponse[]> {
    return apiClient<LatestTelemetryResponse[]>(API_ENDPOINTS.TELEMETRY.LOG(inspectionId));
  },
};

