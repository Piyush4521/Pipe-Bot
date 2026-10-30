export type DriveDirection = 'forward' | 'reverse' | 'stop';

export interface MotorState {
  leftMotorPwm: number;
  rightMotorPwm: number;
  direction: DriveDirection;
  currentDrawAmperes: number;
  isEmergencyStopped: boolean;
}

export interface DriveCommand {
  direction: DriveDirection;
  speedPercentage: number;
  emergencyStop?: boolean;
}

