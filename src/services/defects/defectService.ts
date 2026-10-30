import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { DefectClass, DefectDetection, DefectReviewStatus } from '@/types';

export interface DefectFilterParams {
  inspectionId?: string | number;
  defectClass?: DefectClass | 'all';
  reviewStatus?: DefectReviewStatus | 'all';
  search?: string;
}

export const defectService = {
  async listDefects(params: DefectFilterParams = {}): Promise<DefectDetection[]> {
    const queryParams: Record<string, string | undefined> = {};
    if (params.inspectionId) queryParams.inspection_id = String(params.inspectionId);
    if (params.defectClass && params.defectClass !== 'all') queryParams.defect_class = params.defectClass;
    if (params.reviewStatus && params.reviewStatus !== 'all') queryParams.review_status = params.reviewStatus;
    if (params.search) queryParams.q = params.search;

    const response = await apiClient<DefectDetection[] | { items: DefectDetection[] }>(
      API_ENDPOINTS.DEFECTS.LIST,
      { params: queryParams }
    );
    if (Array.isArray(response)) {
      return response;
    }
    return response?.items ?? [];
  },

  async getDefect(id: string | number): Promise<DefectDetection> {
    return apiClient<DefectDetection>(API_ENDPOINTS.DEFECTS.GET(id));
  },

  async updateReviewStatus(
    id: string | number,
    status: DefectReviewStatus,
    notes?: string
  ): Promise<DefectDetection> {
    return apiClient<DefectDetection>(API_ENDPOINTS.DEFECTS.UPDATE_STATUS(id), {
      method: 'PATCH',
      body: { status, notes },
    });
  },
};
