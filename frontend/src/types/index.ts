export interface Device {
  id: string;
  name: string;
  model: string;
  firmware_version?: string;
  city?: string;
  status: 'online' | 'offline' | 'degraded';
  created_at: string;
  last_seen_at?: string;
  device_metadata: Record<string, any>;
}

export interface TelemetryReading {
  id: number;
  device_id: string;
  ts: string;
  lat?: number;
  lon?: number;
  battery_pct?: number;
  speed_mps?: number;
  temp_c?: number;
  accel_g?: number;
}

export interface Event {
  id: string;
  device_id: string;
  ts: string;
  type: 'LOW_BATTERY' | 'STALE' | 'IMPACT' | 'GEOFENCE';
  severity: 'info' | 'warning' | 'critical';
  payload: Record<string, any>;
  acknowledged_at?: string;
  acknowledged_by?: string;
  created_at: string;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
}
