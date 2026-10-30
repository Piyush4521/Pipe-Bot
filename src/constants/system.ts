export const SYSTEM_INFO = {
  NAME: 'PipeBot',
  FULL_NAME: 'PipeBot Robotic Pipeline Inspection Platform',
  VERSION: '0.1.0-alpha',
  CURRENT_STAGE: 'Stage 5: Final Release Readiness',
  SPECIFICATION: {
    PIPE_TYPE: 'Rigid PVC Pipeline (150 mm to 300 mm)',
    CONTROLLER: 'ESP32-WROOM-32',
    CAMERA: 'AI Thinker ESP32-CAM (OV2640 Module)',
    MOTOR_DRIVER: 'SmartElex 15D Dual DC Motor Driver',
    IMU: 'MPU6050 6-Axis Accelerometer / Gyroscope',
    ENCODERS: 'Dual Optical Wheel Encoders',
    INFERENCE_ENGINE: 'Custom Ultralytics YOLO Defect Model',
    POSITIONING: 'Dual Wheel Rotary Odometry',
  },
} as const;
