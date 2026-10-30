import type { DefectDetectionRecord } from '@/features/defects/types';
import type { InspectionMission } from '@/features/inspection/types';

export interface InspectionReport {
  id: string;
  mission: InspectionMission;
  generatedAt: string;
  inspectorName: string;
  overallRating: 'A' | 'B' | 'C' | 'D' | 'F';
  defectsSummary: {
    total: number;
    critical: number;
    severe: number;
    moderate: number;
    minor: number;
  };
  defects: DefectDetectionRecord[];
}

