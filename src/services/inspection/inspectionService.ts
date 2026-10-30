import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { InspectionRecord, InspectionStatus } from '@/types';

export interface CreateInspectionPayload {
  pipeIdentifier: string;
  pipeDiameterMm: number;
  operatorId: string;
  pipeMaterial?: string;
  notes?: string;
}

export const inspectionService = {
  async listInspections(): Promise<InspectionRecord[]> {
    const response = await apiClient<InspectionRecord[] | { items: InspectionRecord[] }>(
      API_ENDPOINTS.INSPECTIONS.LIST
    );
    if (Array.isArray(response)) {
      return response;
    }
    return response?.items ?? [];
  },

  async getInspection(id: string | number): Promise<InspectionRecord> {
    return apiClient<InspectionRecord>(API_ENDPOINTS.INSPECTIONS.GET(id));
  },

  async createInspection(payload: CreateInspectionPayload): Promise<InspectionRecord> {
    return apiClient<InspectionRecord>(API_ENDPOINTS.INSPECTIONS.CREATE, {
      method: 'POST',
      body: {
        pipeIdentifier: payload.pipeIdentifier,
        pipeDiameterMm: payload.pipeDiameterMm,
        operatorId: payload.operatorId,
        pipeMaterial: payload.pipeMaterial || 'PVC',
        notes: payload.notes || undefined,
      },
    });
  },

  async startInspection(id: string | number): Promise<{ status: InspectionStatus }> {
    return apiClient<{ status: InspectionStatus }>(API_ENDPOINTS.INSPECTIONS.START(id), {
      method: 'POST',
    });
  },

  async stopInspection(id: string | number): Promise<{ status: InspectionStatus }> {
    return apiClient<{ status: InspectionStatus }>(API_ENDPOINTS.INSPECTIONS.STOP(id), {
      method: 'POST',
    });
  },
};
