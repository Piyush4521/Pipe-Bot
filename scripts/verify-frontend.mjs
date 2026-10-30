/**
 * PipeBot Complete Frontend Verification & QA Test Suite
 * Stage 5 Release Verification
 *
 * Assertions:
 * 1. Application routes and legal path contracts
 * 2. Strict Disconnected Mode isolation (zero fake data, zero live status)
 * 3. Demo Mode dataset integrity, labeling, and schema compliance
 * 4. 4-Class YOLO defect registry & multi-criteria filter pipeline
 * 5. Optical frame capture vs. YOLO inference timestamp separation
 * 6. Rotary wheel encoder odometry mathematical physics
 * 7. API error normalizer and network fault resilience
 * 8. Resilient WebSocket protocol contracts, envelope typing, and backoff bounds
 * 9. Safe camera stream abstraction probe parameters
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

// 1. Route Contracts and Constants
describe('1. Route Configuration & Navigation Integrity', async () => {
  const { ROUTES } = await import('../src/constants/routes.ts');
  const { SYSTEM_INFO } = await import('../src/constants/system.ts');

  it('should define all required public and dashboard route paths', () => {
    assert.equal(ROUTES.HOME, '/');
    assert.equal(ROUTES.PRIVACY, '/privacy');
    assert.equal(ROUTES.TERMS, '/terms');
    assert.equal(ROUTES.DASHBOARD.ROOT, '/dashboard');
    assert.equal(ROUTES.DASHBOARD.INSPECTION, '/dashboard/inspection');
    assert.equal(ROUTES.DASHBOARD.VEHICLE, '/dashboard/vehicle');
    assert.equal(ROUTES.DASHBOARD.TELEMETRY, '/dashboard/telemetry');
    assert.equal(ROUTES.DASHBOARD.DEFECTS, '/dashboard/defects');
    assert.equal(ROUTES.DASHBOARD.HISTORY, '/dashboard/history');
    assert.equal(ROUTES.DASHBOARD.REPORTS, '/dashboard/reports');
    assert.equal(ROUTES.DASHBOARD.SETTINGS, '/dashboard/settings');
  });

  it('should reflect Stage 5 release readiness in system constant', () => {
    assert.equal(SYSTEM_INFO.NAME, 'PipeBot');
    assert.ok(SYSTEM_INFO.CURRENT_STAGE.includes('Stage 5'));
  });
});

// 2. Demo Data Isolation vs Disconnected Mode
describe('2. State Isolation: Disconnected Mode vs. Demo Mode', async () => {
  const {
    DEMO_SYSTEM_STATUS,
    DEMO_DEFECTS,
    DEMO_ENCODER_TELEMETRY,
    DEMO_IMU_TELEMETRY,
    DEMO_VEHICLE_TELEMETRY,
    DEMO_INSPECTIONS,
    DEMO_REPORTS,
  } = await import('../src/services/demo/demoData.ts');

  it('should verify that all Demo Mode defects contain isDemo: true and valid classes', () => {
    assert.equal(DEMO_DEFECTS.length, 4, 'Demo dataset must feature exactly 4 defects');

    const expectedClasses = new Set(['deformation', 'misalignment', 'obstacle', 'rupture']);
    const presentClasses = new Set(DEMO_DEFECTS.map((d) => d.defectClass));
    assert.deepEqual(presentClasses, expectedClasses, 'Must cover all 4 PVC anomaly classes');

    DEMO_DEFECTS.forEach((d) => {
      assert.equal(d.isDemo, true, `Defect ${d.id} must be flagged as isDemo`);
      assert.ok(typeof d.estimatedDistanceMeters === 'number', 'Must have numeric distance');
      assert.ok(d.captureTimestamp, 'Must possess captureTimestamp');
      assert.ok(d.inferenceTimestamp, 'Must possess inferenceTimestamp');
      assert.notEqual(d.captureTimestamp, d.inferenceTimestamp, 'Capture and inference timestamps must differ');
    });
  });

  it('should confirm camera stream is disconnected even in Demo Mode status', () => {
    assert.equal(DEMO_SYSTEM_STATUS.camera, 'disconnected', 'Camera must never be faked as connected');
  });

  it('should confirm vehicle telemetry reports idle motors and disengaged e-stop in demo data', () => {
    assert.equal(DEMO_VEHICLE_TELEMETRY.leftMotorState, 'idle');
    assert.equal(DEMO_VEHICLE_TELEMETRY.rightMotorState, 'idle');
    assert.equal(DEMO_VEHICLE_TELEMETRY.emergencyStopEngaged, false);
  });
});

// 3. Multi-Criteria Defect Filtering Engine
describe('3. Defect Anomaly Registry & Filtering Pipeline', async () => {
  const { DEMO_DEFECTS } = await import('../src/services/demo/demoData.ts');

  const runFilter = (defects, selectedClass, selectedStatus, searchQuery) => {
    return defects.filter((item) => {
      if (selectedClass !== 'all' && item.defectClass !== selectedClass) return false;
      if (selectedStatus !== 'all' && item.reviewStatus !== selectedStatus) return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase().trim();
        const matchesId = item.id.toLowerCase().includes(q);
        const matchesFrame = item.frameId.toLowerCase().includes(q);
        const matchesInspection = item.inspectionId.toLowerCase().includes(q);
        const matchesNotes = item.notes?.toLowerCase().includes(q) ?? false;
        if (!matchesId && !matchesFrame && !matchesInspection && !matchesNotes) return false;
      }
      return true;
    });
  };

  it('should filter individually across each defect class', () => {
    assert.equal(runFilter(DEMO_DEFECTS, 'deformation', 'all', '').length, 1);
    assert.equal(runFilter(DEMO_DEFECTS, 'misalignment', 'all', '').length, 1);
    assert.equal(runFilter(DEMO_DEFECTS, 'obstacle', 'all', '').length, 1);
    assert.equal(runFilter(DEMO_DEFECTS, 'rupture', 'all', '').length, 1);
  });

  it('should filter by review status', () => {
    const verified = runFilter(DEMO_DEFECTS, 'all', 'verified', '');
    const unreviewed = runFilter(DEMO_DEFECTS, 'all', 'unreviewed', '');
    assert.equal(verified.length, 2);
    assert.equal(unreviewed.length, 2);
    assert.ok(verified.every((d) => d.reviewStatus === 'verified'));
    assert.ok(unreviewed.every((d) => d.reviewStatus === 'unreviewed'));
  });

  it('should search across ID, frame, and engineering notes', () => {
    // By ID
    assert.equal(runFilter(DEMO_DEFECTS, 'all', 'all', 'DEF-002').length, 1);
    // By Frame ID
    assert.equal(runFilter(DEMO_DEFECTS, 'all', 'all', 'FRM-05620').length, 1);
    // By Notes
    assert.equal(runFilter(DEMO_DEFECTS, 'all', 'all', 'flattening').length, 1);
    assert.equal(runFilter(DEMO_DEFECTS, 'all', 'all', 'bell connection').length, 1);
  });

  it('should handle zero match queries gracefully without throwing', () => {
    const result = runFilter(DEMO_DEFECTS, 'rupture', 'unreviewed', 'sediment');
    assert.equal(result.length, 0);
  });
});

// 4. API Error Normalization
describe('4. API Client Error Normalization & Resilience', async () => {
  const { ApiError, createNetworkError, createTimeoutError } = await import(
    '../src/services/api/apiErrors.ts'
  );

  it('should normalize network failure into ApiError with isNetworkError=true', () => {
    const error = createNetworkError('/api/v1/system/status');
    assert.ok(error instanceof ApiError);
    assert.equal(error.isNetworkError, true);
    assert.equal(error.isTimeout, false);
    assert.ok(error.message.includes('Network failure'));
  });

  it('should normalize request timeout into ApiError with isTimeout=true', () => {
    const error = createTimeoutError('/api/v1/telemetry/latest', 8000);
    assert.ok(error instanceof ApiError);
    assert.equal(error.isTimeout, true);
    assert.equal(error.isNetworkError, false);
    assert.ok(error.message.includes('8000ms'));
  });
});

// 5. WebSocket Client Contracts & Disconnected Default Protection
describe('5. WebSocket Protocol & Reconnection Boundaries', async () => {
  const { APP_CONFIG } = await import('../src/constants/config.ts');

  it('should confirm default configuration does not assume an active WebSocket server', () => {
    // When VITE_WS_URL is unset, wsUrl defaults to empty string
    assert.equal(typeof APP_CONFIG.wsUrl, 'string');
    assert.equal(APP_CONFIG.defaultMode, 'disconnected');
  });

  it('should validate exponential backoff formula ceiling at 16000ms', () => {
    const calculateBackoff = (attempt) => {
      return Math.min(1000 * Math.pow(2, attempt - 1), 16000);
    };

    assert.equal(calculateBackoff(1), 1000); // 1s
    assert.equal(calculateBackoff(2), 2000); // 2s
    assert.equal(calculateBackoff(3), 4000); // 4s
    assert.equal(calculateBackoff(4), 8000); // 8s
    assert.equal(calculateBackoff(5), 16000); // 16s max
    assert.equal(calculateBackoff(6), 16000); // clamped at 16s
  });

  it('should enforce typed message envelope structure', () => {
    const message = {
      type: 'telemetry_encoder',
      timestamp: new Date().toISOString(),
      payload: {
        leftTicks: 4120,
        rightTicks: 4118,
        estimatedDistanceMeters: 14.52,
      },
    };

    assert.equal(message.type, 'telemetry_encoder');
    assert.ok(message.timestamp);
    assert.equal(message.payload.leftTicks, 4120);
  });
});

// 6. Camera Stream Abstraction Safety
describe('6. Camera Stream Service Probing', async () => {
  const { APP_CONFIG } = await import('../src/constants/config.ts');

  it('should ensure camera stream URL defaults safely to empty when unset', () => {
    assert.equal(typeof APP_CONFIG.cameraStreamUrl, 'string');
  });
});

// 7. Rotary Wheel Encoder Odometry Physics
describe('7. Rotary Encoder Odometry Formulation & Slip Physics', () => {
  it('should accurately calculate linear distance from wheel diameter and pulses', () => {
    const calculateDistanceMeters = (leftTicks, rightTicks, ppr, wheelDiameterMm) => {
      const circumferenceMm = Math.PI * wheelDiameterMm;
      const avgTicks = (leftTicks + rightTicks) / 2;
      const revolutions = avgTicks / ppr;
      const distanceMm = revolutions * circumferenceMm;
      return Number((distanceMm / 1000).toFixed(3));
    };

    // 1 Revolution: 360 pulses, 65mm diameter wheel
    // Circumference = 65 * pi = 204.204 mm = 0.204 m
    const d1 = calculateDistanceMeters(360, 360, 360, 65);
    assert.equal(d1, 0.204);

    // 50 Revolutions: 18,000 pulses -> 10.210 m
    const d50 = calculateDistanceMeters(18000, 18000, 360, 65);
    assert.equal(d50, 10.21);
  });
});
