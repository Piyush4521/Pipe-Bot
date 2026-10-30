import { createContext, useContext, useState, useMemo, type FC, type ReactNode } from 'react';
import { APP_CONFIG, type AppMode } from '@/constants/config';
import type {
  DefectDetection,
  EncoderTelemetry,
  IMUTelemetry,
  InspectionRecord,
  ReportRecord,
  SystemConnectionStatus,
  VehicleTelemetry,
} from '@/types';
import {
  DEMO_DEFECTS,
  DEMO_ENCODER_TELEMETRY,
  DEMO_IMU_TELEMETRY,
  DEMO_INSPECTIONS,
  DEMO_REPORTS,
  DEMO_SYSTEM_STATUS,
  DEMO_VEHICLE_TELEMETRY,
} from '@/services/demo/demoData';

export interface AppContextValue {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  toggleDemoMode: () => void;
  isDemoMode: boolean;
  systemStatus: SystemConnectionStatus;
  encoderTelemetry: EncoderTelemetry;
  imuTelemetry: IMUTelemetry;
  vehicleTelemetry: VehicleTelemetry;
  defects: DefectDetection[];
  inspections: InspectionRecord[];
  reports: ReportRecord[];
  connectionError: string | null;
}

const DISCONNECTED_SYSTEM_STATUS: SystemConnectionStatus = {
  hardware: 'disconnected',
  camera: 'disconnected',
  backend: 'disconnected',
  aiProcessing: 'disconnected',
  lastHeartbeatTimestamp: null,
};

const DISCONNECTED_ENCODER: EncoderTelemetry = {
  leftTicks: null,
  rightTicks: null,
  leftRpm: null,
  rightRpm: null,
  estimatedDistanceMeters: null,
  timestamp: null,
};

const DISCONNECTED_IMU: IMUTelemetry = {
  accelX: null,
  accelY: null,
  accelZ: null,
  gyroX: null,
  gyroY: null,
  gyroZ: null,
  pitchDegrees: null,
  rollDegrees: null,
  timestamp: null,
};

const DISCONNECTED_VEHICLE: VehicleTelemetry = {
  controllerState: 'disconnected',
  motorDriverState: 'disconnected',
  leftMotorState: 'offline',
  rightMotorState: 'offline',
  emergencyStopEngaged: false,
  commandAckState: 'idle',
  batteryVoltage: null,
  currentDrawAmperes: null,
};

const AppContext = createContext<AppContextValue | null>(null);

export interface AppProviderProps {
  children: ReactNode;
  initialMode?: AppMode;
}

export const AppProvider: FC<AppProviderProps> = ({
  children,
  initialMode = APP_CONFIG.defaultMode,
}) => {
  const [mode, setMode] = useState<AppMode>(initialMode);
  const [connectionError] = useState<string | null>(null);

  const toggleDemoMode = () => {
    setMode((prev) => (prev === 'demo' ? 'disconnected' : 'demo'));
  };

  const isDemoMode = mode === 'demo';

  const systemStatus = useMemo(() => {
    if (mode === 'demo') return DEMO_SYSTEM_STATUS;
    return DISCONNECTED_SYSTEM_STATUS;
  }, [mode]);

  const encoderTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_ENCODER_TELEMETRY;
    return DISCONNECTED_ENCODER;
  }, [mode]);

  const imuTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_IMU_TELEMETRY;
    return DISCONNECTED_IMU;
  }, [mode]);

  const vehicleTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_VEHICLE_TELEMETRY;
    return DISCONNECTED_VEHICLE;
  }, [mode]);

  const defects = useMemo(() => {
    if (mode === 'demo') return DEMO_DEFECTS;
    return [];
  }, [mode]);

  const inspections = useMemo(() => {
    if (mode === 'demo') return DEMO_INSPECTIONS;
    return [];
  }, [mode]);

  const reports = useMemo(() => {
    if (mode === 'demo') return DEMO_REPORTS;
    return [];
  }, [mode]);

  const contextValue: AppContextValue = {
    mode,
    setMode,
    toggleDemoMode,
    isDemoMode,
    systemStatus,
    encoderTelemetry,
    imuTelemetry,
    vehicleTelemetry,
    defects,
    inspections,
    reports,
    connectionError,
  };

  return <AppContext.Provider value={contextValue}>{children}</AppContext.Provider>;
};

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export function useAppMode() {
  const { mode, setMode, toggleDemoMode, isDemoMode } = useAppContext();
  return { mode, setMode, toggleDemoMode, isDemoMode };
}

export function useSystemStatus() {
  const { systemStatus, connectionError } = useAppContext();
  return { systemStatus, connectionError };
}

export function useTelemetry() {
  const { encoderTelemetry, imuTelemetry, vehicleTelemetry } = useAppContext();
  return { encoderTelemetry, imuTelemetry, vehicleTelemetry };
}

export function useDefects() {
  const { defects, isDemoMode } = useAppContext();
  return { defects, isDemoMode };
}

export function useInspection() {
  const { inspections, isDemoMode } = useAppContext();
  return { inspections, isDemoMode };
}
