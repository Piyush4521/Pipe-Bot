export * from './navigation';

export type SystemHealthStatus = 'healthy' | 'warning' | 'critical' | 'offline' | 'idle';

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

// 1. Connection & System Status Models
export type ConnectionState =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'timeout'
  | 'error';

export interface SystemConnectionStatus {
  hardware: ConnectionState;
  camera: ConnectionState;
  backend: ConnectionState;
  aiProcessing: ConnectionState;
  lastHeartbeatTimestamp: string | null;
  errorMessage?: string;
}

// 2. Inspection Session Models
export type InspectionStatus = 'idle' | 'running' | 'paused' | 'completed' | 'aborted';

export interface InspectionRecord extends BaseEntity {
  inspectionId: string;
  pipeIdentifier: string;
  pipeDiameterMm: number;
  operatorId: string;
  startedAt: string;
  completedAt?: string | null;
  totalDistanceMeters: number | null;
  defectCount: number;
  status: InspectionStatus;
  pipeMaterial?: string;
  notes?: string | null;
  isArchived?: boolean;
}

// 3. Optical Frame Metadata (Capture-Time Telemetry Association)
export interface FrameMetadata {
  frameId: string;
  captureTimestamp: string;
  encoderLeftTicks: number | null;
  encoderRightTicks: number | null;
  estimatedDistanceMeters: number | null;
}

// 4. Target Defect Classifications and Detection Models
export type DefectClass =
  | 'Deformation'
  | 'Misalignment'
  | 'Obstacle'
  | 'Rupture'
  | 'deformation'
  | 'misalignment'
  | 'obstacle'
  | 'rupture';
export type DefectType = DefectClass;
export type DefectSeverity = 'minor' | 'moderate' | 'severe' | 'critical';
export type DefectReviewStatus =
  | 'unreviewed'
  | 'verified'
  | 'dismissed'
  | 'pending'
  | 'confirmed'
  | 'rejected';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DefectDetection extends BaseEntity {
  defectId?: string;
  inspectionId: string;
  defectClass: DefectClass;
  confidence: number | null;
  frameId: string;
  captureTimestamp: string; // Time recorded on optical capture module
  inferenceTimestamp: string | null; // Time evaluated by YOLO model on server
  eventArrivalTimestamp?: string; // Time packet received by operator dashboard
  estimatedDistanceMeters: number | null; // Correlated from encoder pulses at capture time
  reviewStatus: DefectReviewStatus;
  boundingBox?: BoundingBox;
  snapshotUrl?: string;
  notes?: string;
  isDemo?: boolean; // Flag to guarantee demo isolation
}

// Backward compatibility alias
export type DefectItem = DefectDetection;

// 5. Rotary Encoder Odometry Models
export interface EncoderTelemetry {
  leftTicks: number | null;
  rightTicks: number | null;
  leftRpm: number | null;
  rightRpm: number | null;
  estimatedDistanceMeters: number | null;
  timestamp: string | null;
}

// 6. MPU6050 Inertial Measurement Models
export interface IMUTelemetry {
  accelX: number | null;
  accelY: number | null;
  accelZ: number | null;
  gyroX: number | null;
  gyroY: number | null;
  gyroZ: number | null;
  pitchDegrees: number | null;
  rollDegrees: number | null;
  timestamp: string | null;
}

// 7. Vehicle Actuation and Safety State
export type MotorActuationState = 'idle' | 'forward' | 'reverse' | 'offline';
export type CommandAckState = 'idle' | 'pending' | 'acknowledged' | 'rejected';

export interface VehicleTelemetry {
  controllerState: ConnectionState;
  motorDriverState: ConnectionState;
  leftMotorState: MotorActuationState;
  rightMotorState: MotorActuationState;
  emergencyStopEngaged: boolean;
  commandAckState: CommandAckState;
  batteryVoltage: number | null;
  currentDrawAmperes: number | null;
  lastCommandTimestamp?: string;
}

// 8. Compliance & Engineering Report Models
export interface ReportRecord extends BaseEntity {
  reportId: string;
  inspectionId: string;
  pipeIdentifier: string;
  generatedAt: string;
  defectCount: number;
  overallRating: 'A' | 'B' | 'C' | 'D' | 'F';
  status: 'draft' | 'finalized' | 'archived';
  fileSizeKb?: number;
}
