export interface HardwareConfig {
  esp32Host: string;
  esp32Port: number;
  camStreamUrl: string;
  wheelDiameterMm: number;
  encoderPulsesPerRev: number;
}

export interface BackendConfig {
  apiBaseUrl: string;
  websocketUrl: string;
  yoloConfidenceThreshold: number;
}

