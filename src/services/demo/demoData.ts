/**
 * Controlled Representative Demo Dataset for Dashboard Testing
 *
 * IMPORTANT:
 * This data is explicitly flagged as DEMO DATA for frontend interaction verification.
 * It is isolated and never mixed with real inspection records.
 */

import type {
  DefectDetection,
  EncoderTelemetry,
  IMUTelemetry,
  InspectionRecord,
  ReportRecord,
  SystemConnectionStatus,
  VehicleTelemetry,
} from '@/types';

export const DEMO_SYSTEM_STATUS: SystemConnectionStatus = {
  hardware: 'connected',
  camera: 'disconnected', // Camera remains disconnected even in demo
  backend: 'connected',
  aiProcessing: 'connected',
  lastHeartbeatTimestamp: '2026-10-30T10:30:00.000Z',
};

export const DEMO_ENCODER_TELEMETRY: EncoderTelemetry = {
  leftTicks: 4120,
  rightTicks: 4118,
  leftRpm: 42.5,
  rightRpm: 42.3,
  estimatedDistanceMeters: 14.52,
  timestamp: '2026-10-30T10:30:00.000Z',
};

export const DEMO_IMU_TELEMETRY: IMUTelemetry = {
  accelX: 0.02,
  accelY: -0.01,
  accelZ: 0.98,
  gyroX: 0.1,
  gyroY: -0.2,
  gyroZ: 0.0,
  pitchDegrees: 1.8, // 1.8 deg conduit gradient
  rollDegrees: -0.4,
  timestamp: '2026-10-30T10:30:00.000Z',
};

export const DEMO_VEHICLE_TELEMETRY: VehicleTelemetry = {
  controllerState: 'connected',
  motorDriverState: 'connected',
  leftMotorState: 'idle',
  rightMotorState: 'idle',
  emergencyStopEngaged: false,
  commandAckState: 'idle',
  batteryVoltage: 12.4,
  currentDrawAmperes: 0.35,
};

export const DEMO_INSPECTIONS: InspectionRecord[] = [
  {
    id: 'demo-run-001',
    inspectionId: 'INS-2026-001',
    pipeIdentifier: 'PVC-LN-200-EAST',
    pipeDiameterMm: 200,
    operatorId: 'ENG-TECH-04',
    startedAt: '2026-10-30 10:10:00',
    completedAt: '2026-10-30 10:28:15',
    totalDistanceMeters: 28.5,
    defectCount: 4,
    status: 'completed',
    createdAt: '2026-10-30T10:10:00.000Z',
    updatedAt: '2026-10-30T10:28:15.000Z',
  },
];

export const DEMO_DEFECTS: DefectDetection[] = [
  {
    id: 'DEF-001',
    inspectionId: 'INS-2026-001',
    frameId: 'FRM-01420',
    defectClass: 'deformation',
    confidence: 0.88,
    captureTimestamp: '2026-10-30 10:14:02.120',
    inferenceTimestamp: '2026-10-30 10:14:02.195',
    estimatedDistanceMeters: 6.4,
    reviewStatus: 'unreviewed',
    boundingBox: { x: 120, y: 80, width: 140, height: 95 },
    notes: 'Radial pipe flattening under soil load',
    isDemo: true,
    createdAt: '2026-10-30T10:14:02.120Z',
    updatedAt: '2026-10-30T10:14:02.120Z',
  },
  {
    id: 'DEF-002',
    inspectionId: 'INS-2026-001',
    frameId: 'FRM-02880',
    defectClass: 'misalignment',
    confidence: 0.92,
    captureTimestamp: '2026-10-30 10:18:45.450',
    inferenceTimestamp: '2026-10-30 10:18:45.520',
    estimatedDistanceMeters: 13.15,
    reviewStatus: 'verified',
    boundingBox: { x: 210, y: 140, width: 180, height: 110 },
    notes: 'Joint deflection at segment 4 bell connection',
    isDemo: true,
    createdAt: '2026-10-30T10:18:45.450Z',
    updatedAt: '2026-10-30T10:18:45.450Z',
  },
  {
    id: 'DEF-003',
    inspectionId: 'INS-2026-001',
    frameId: 'FRM-04100',
    defectClass: 'obstacle',
    confidence: 0.79,
    captureTimestamp: '2026-10-30 10:22:10.810',
    inferenceTimestamp: '2026-10-30 10:22:10.890',
    estimatedDistanceMeters: 19.8,
    reviewStatus: 'unreviewed',
    boundingBox: { x: 90, y: 190, width: 220, height: 80 },
    notes: 'Sediment buildup on pipe invert',
    isDemo: true,
    createdAt: '2026-10-30T10:22:10.810Z',
    updatedAt: '2026-10-30T10:22:10.810Z',
  },
  {
    id: 'DEF-004',
    inspectionId: 'INS-2026-001',
    frameId: 'FRM-05620',
    defectClass: 'rupture',
    confidence: 0.95,
    captureTimestamp: '2026-10-30 10:26:30.300',
    inferenceTimestamp: '2026-10-30 10:26:30.380',
    estimatedDistanceMeters: 26.4,
    reviewStatus: 'verified',
    boundingBox: { x: 160, y: 110, width: 160, height: 140 },
    notes: 'Longitudinal wall crack with hairline branching',
    isDemo: true,
    createdAt: '2026-10-30T10:26:30.300Z',
    updatedAt: '2026-10-30T10:26:30.300Z',
  },
];

export const DEMO_REPORTS: ReportRecord[] = [
  {
    id: 'demo-rep-001',
    reportId: 'REP-2026-001',
    inspectionId: 'INS-2026-001',
    pipeIdentifier: 'PVC-LN-200-EAST',
    generatedAt: '2026-10-30 10:35:00',
    defectCount: 4,
    overallRating: 'C',
    status: 'draft',
    fileSizeKb: 842,
    createdAt: '2026-10-30T10:35:00.000Z',
    updatedAt: '2026-10-30T10:35:00.000Z',
  },
];

