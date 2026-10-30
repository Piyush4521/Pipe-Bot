import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  type FC,
  type ReactNode,
} from 'react';
import { APP_CONFIG, type AppMode } from '@/constants/config';
import type {
  DefectDetection,
  DefectReviewStatus,
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
import { connectionService } from '@/services/connection/connectionService';
import { inspectionService, type CreateInspectionPayload } from '@/services/inspection/inspectionService';
import { defectService } from '@/services/defects/defectService';
import { telemetryService } from '@/services/telemetry/telemetryService';
import { globalWebSocket, type WebSocketMessage } from '@/services/websocket/webSocketClient';

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
  backendOnline: boolean;
  isRefreshing: boolean;
  refreshData: () => Promise<void>;
  createInspection: (payload: CreateInspectionPayload) => Promise<InspectionRecord>;
  updateDefectStatus: (id: string | number, status: DefectReviewStatus, notes?: string) => Promise<void>;
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
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Live data states populated from backend REST/WebSocket
  const [liveSystemStatus, setLiveSystemStatus] = useState<SystemConnectionStatus>(DISCONNECTED_SYSTEM_STATUS);
  const [liveInspections, setLiveInspections] = useState<InspectionRecord[]>([]);
  const [liveDefects, setLiveDefects] = useState<DefectDetection[]>([]);
  const [liveReports] = useState<ReportRecord[]>([]);
  const [liveEncoder, setLiveEncoder] = useState<EncoderTelemetry>(DISCONNECTED_ENCODER);
  const [liveImu, setLiveImu] = useState<IMUTelemetry>(DISCONNECTED_IMU);
  const [liveVehicle, setLiveVehicle] = useState<VehicleTelemetry>(DISCONNECTED_VEHICLE);

  const toggleDemoMode = () => {
    setMode((prev) => (prev === 'demo' ? 'disconnected' : 'demo'));
  };

  const isDemoMode = mode === 'demo';

  // Fetch real data from backend when in live or disconnected mode
  const refreshData = useCallback(async () => {
    if (mode === 'demo') {
      return;
    }
    setIsRefreshing(true);
    try {
      // 1. Query system status
      const statusRes = await connectionService.getSystemStatus();
      setLiveSystemStatus(statusRes);
      setBackendOnline(statusRes.backend === 'connected');
      setConnectionError(null);

      // 2. Query inspections from database
      try {
        const inspList = await inspectionService.listInspections();
        setLiveInspections(inspList);
      } catch (err) {
        console.warn('Unable to load inspections:', err);
      }

      // 3. Query defects from database
      try {
        const defectList = await defectService.listDefects();
        setLiveDefects(defectList);
      } catch (err) {
        console.warn('Unable to load defects:', err);
      }

      // 4. Query latest telemetry snapshot
      try {
        const teleRes = await telemetryService.getLatestTelemetry();
        if (teleRes.encoder) setLiveEncoder(teleRes.encoder);
        if (teleRes.imu) setLiveImu(teleRes.imu);
        if (teleRes.vehicle) setLiveVehicle(teleRes.vehicle);
      } catch (err) {
        console.warn('Unable to load telemetry:', err);
      }
    } catch (err: unknown) {
      setBackendOnline(false);
      setLiveSystemStatus(DISCONNECTED_SYSTEM_STATUS);
      const errMsg = err instanceof Error ? err.message : 'Backend unreachable';
      setConnectionError(errMsg);
    } finally {
      setIsRefreshing(false);
    }
  }, [mode]);

  // Initial load
  useEffect(() => {
    if (mode !== 'demo') {
      refreshData();
    }
  }, [mode, refreshData]);

  // Duplex WebSocket ingestion
  useEffect(() => {
    if (mode === 'demo') {
      globalWebSocket.disconnect();
      return;
    }

    globalWebSocket.connect();

    const unsubscribe = globalWebSocket.subscribe((msg: WebSocketMessage) => {
      if (msg.type === 'system_status') {
        setLiveSystemStatus(msg.payload as SystemConnectionStatus);
      } else if (msg.type === 'telemetry_encoder') {
        setLiveEncoder(msg.payload as EncoderTelemetry);
      } else if (msg.type === 'telemetry_imu') {
        setLiveImu(msg.payload as IMUTelemetry);
      } else if (msg.type === 'vehicle_status') {
        setLiveVehicle(msg.payload as VehicleTelemetry);
      } else if (msg.type === 'defect_detected') {
        const newDefect = msg.payload as DefectDetection;
        setLiveDefects((prev) => [newDefect, ...prev]);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [mode]);

  const createInspection = useCallback(async (payload: CreateInspectionPayload) => {
    const created = await inspectionService.createInspection(payload);
    setLiveInspections((prev) => [created, ...prev]);
    return created;
  }, []);

  const updateDefectStatus = useCallback(
    async (id: string | number, status: DefectReviewStatus, notes?: string) => {
      const updated = await defectService.updateReviewStatus(id, status, notes);
      setLiveDefects((prev) =>
        prev.map((d) =>
          String(d.id) === String(id) || d.defectId === String(id)
            ? { ...d, ...updated }
            : d
        )
      );
    },
    []
  );

  const systemStatus = useMemo(() => {
    if (mode === 'demo') return DEMO_SYSTEM_STATUS;
    return liveSystemStatus;
  }, [mode, liveSystemStatus]);

  const encoderTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_ENCODER_TELEMETRY;
    return liveEncoder;
  }, [mode, liveEncoder]);

  const imuTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_IMU_TELEMETRY;
    return liveImu;
  }, [mode, liveImu]);

  const vehicleTelemetry = useMemo(() => {
    if (mode === 'demo') return DEMO_VEHICLE_TELEMETRY;
    return liveVehicle;
  }, [mode, liveVehicle]);

  const defects = useMemo(() => {
    if (mode === 'demo') return DEMO_DEFECTS;
    return liveDefects;
  }, [mode, liveDefects]);

  const inspections = useMemo(() => {
    if (mode === 'demo') return DEMO_INSPECTIONS;
    return liveInspections;
  }, [mode, liveInspections]);

  const reports = useMemo(() => {
    if (mode === 'demo') return DEMO_REPORTS;
    return liveReports;
  }, [mode, liveReports]);

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
    backendOnline,
    isRefreshing,
    refreshData,
    createInspection,
    updateDefectStatus,
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
  const { systemStatus, connectionError, backendOnline, isRefreshing, refreshData } = useAppContext();
  return { systemStatus, connectionError, backendOnline, isRefreshing, refreshData };
}

export function useTelemetry() {
  const { encoderTelemetry, imuTelemetry, vehicleTelemetry } = useAppContext();
  return { encoderTelemetry, imuTelemetry, vehicleTelemetry };
}

export function useDefects() {
  const { defects, isDemoMode, updateDefectStatus } = useAppContext();
  return { defects, isDemoMode, updateDefectStatus };
}

export function useInspection() {
  const { inspections, isDemoMode, createInspection, refreshData, isRefreshing } = useAppContext();
  return { inspections, isDemoMode, createInspection, refreshData, isRefreshing };
}
