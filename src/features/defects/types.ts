import type { DefectSeverity, DefectType } from '@/types';

export interface BoundingBox2D {
  xMin: number;
  yMin: number;
  xMax: number;
  yMax: number;
}

export interface DefectDetectionRecord {
  id: string;
  missionId: string;
  type: DefectType;
  severity: DefectSeverity;
  confidence: number;
  distanceMarkerMeters: number;
  timestamp: string;
  box: BoundingBox2D;
  snapshotPath?: string;
  notes?: string;
}

