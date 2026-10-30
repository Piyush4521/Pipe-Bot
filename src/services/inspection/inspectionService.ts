import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { InspectionRecord, InspectionStatus } from '@/types';

export interface CreateInspectionPayload {
  pipeIdentifier: string;
  pipeDiameterMm: number;
  operatorId: string;
}

export const inspectionService = {
  async listInspections(): Promise<InspectionRecord[]> {
    return apiClient<InspectionRecord[]>(API_ENDPOINTS.INSPECTIONS.LIST);
  },

  async getInspection(id: string): Promise<InspectionRecord> {
    return apiClient<InspectionRecord>(API_ENDPOINTS.INSPECTIONS.GET(id));
  },

  async createInspection(payload: CreateInspectionPayload): Promise<InspectionRecord> {
    return apiClient<InspectionRecord>(API_ENDPOINTS.INSPECTIONS.CREATE, {
      method: 'POST',
      body: payload,
    });
  },

  async startInspection(id: string): Promise<{ status: InspectionStatus }> {
    return apiClient<{ status: InspectionStatus }>(API_ENDPOINTS.INSPECTIONS.START(id), {
      method: 'POST',
    });
  },

  async stopInspection(id: string): Promise<{ status: InspectionStatus }> {
    return apiClient<{ status: InspectionStatus }>(API_ENDPOINTS.INSPECTIONS.STOP(id), {
      method: 'POST',
    });
  },
};

