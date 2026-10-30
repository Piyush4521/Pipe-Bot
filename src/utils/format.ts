/**
 * Technical formatting utilities for industrial telemetry and timestamps.
 */

export function formatDistance(distanceMeters: number | null | undefined): string {
  if (distanceMeters === null || distanceMeters === undefined) {
    return '0.00 m';
  }
  return `${distanceMeters.toFixed(2)} m`;
}

export function formatIsoTimestamp(date: Date | string | number): string {
  const d = new Date(date);
  return d.toISOString().replace('T', ' ').substring(0, 19);
}

export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '0.0%';
  }
  return `${value.toFixed(1)}%`;
}

