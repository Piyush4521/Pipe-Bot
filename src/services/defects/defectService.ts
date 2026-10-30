import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { DefectClass, DefectDetection, DefectReviewStatus } from '@/types';

export interface DefectFilterParams {
  inspectionId?: string;
  defectClass?: DefectClass | 'all';
  reviewStatus?: DefectReviewStatus | 'all';
  search?: string;
}

export const defectService = {
  async listDefects(params: DefectFilterParams = {}): Promise<DefectDetection[]> {
    const queryParams: Record<string, string | undefined> = {};
    if (params.inspectionId) queryParams.inspectionId = params.inspectionId;
    if (params.defectClass && params.defectClass !== 'all') queryParams.class = params.defectClass;
    if (params.reviewStatus && params.reviewStatus !== 'all') queryParams.status = params.reviewStatus;
    if (params.search) queryParams.q = params.search;

    return apiClient<DefectDetection[]>(API_ENDPOINTS.DEFECTS.LIST, { params: queryParams });
  },

  async getDefect(id: string): Promise<DefectDetection> {
    return apiClient<DefectDetection>(API_ENDPOINTS.DEFECTS.GET(id));
  },

  async updateReviewStatus(
    id: string,
    status: DefectReviewStatus,
    notes?: string
  ): Promise<DefectDetection> {
    return apiClient<DefectDetection>(API_ENDPOINTS.DEFECTS.UPDATE_STATUS(id), {
      method: 'PATCH',
      body: { status, notes },
    });
  },
};

