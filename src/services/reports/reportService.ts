import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/endpoints';
import type { ReportRecord } from '@/types';

export const reportService = {
  async listReports(): Promise<ReportRecord[]> {
    return apiClient<ReportRecord[]>(API_ENDPOINTS.REPORTS.LIST);
  },

  async getReport(id: string): Promise<ReportRecord> {
    return apiClient<ReportRecord>(API_ENDPOINTS.REPORTS.GET(id));
  },

  async generateReport(inspectionId: string): Promise<ReportRecord> {
    return apiClient<ReportRecord>(API_ENDPOINTS.REPORTS.GENERATE, {
      method: 'POST',
      body: { inspectionId },
    });
  },
};

