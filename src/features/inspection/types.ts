export type MissionStatus = 'idle' | 'in_progress' | 'paused' | 'completed' | 'aborted';

export interface InspectionMission {
  id: string;
  pipeIdentifier: string;
  pipeMaterial: 'PVC' | 'HDPE' | 'Concrete';
  pipeDiameterMm: number;
  operatorId: string;
  startedAt: string;
  completedAt?: string;
  status: MissionStatus;
  totalDistanceMeters: number;
  defectCount: number;
}

