export interface TelemetryPacket {
  packetId: number;
  timestamp: string;
  encoderTicks: number;
  calculatedDistanceMeters: number;
  linearVelocityMps: number;
  batteryVoltageVolts: number;
  batteryPercentage: number;
  temperatureCelsius: number;
  wifiRssiDbm: number;
}

