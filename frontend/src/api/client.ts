import type { Device, TelemetryReading, Event } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Devices
  async getDevices(): Promise<Device[]> {
    return this.request<Device[]>('/devices');
  }

  async getDevice(deviceId: string): Promise<Device> {
    return this.request<Device>(`/devices/${deviceId}`);
  }

  // Telemetry
  async getTelemetry(params: {
    device_id: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }): Promise<TelemetryReading[]> {
    const query = new URLSearchParams();
    if (params.start_time) query.append('start_time', params.start_time);
    if (params.end_time) query.append('end_time', params.end_time);
    if (params.limit) query.append('limit', params.limit.toString());

    const queryString = query.toString();
    const endpoint = `/devices/${params.device_id}/telemetry${queryString ? `?${queryString}` : ''}`;
    return this.request<TelemetryReading[]>(endpoint);
  }

  async getLatestTelemetry(deviceId: string): Promise<TelemetryReading | null> {
    const readings = await this.getTelemetry({ device_id: deviceId, limit: 1 });
    return readings[0] || null;
  }

  // Events
  async getEvents(params: {
    device_id?: string;
    type?: string;
    severity?: string;
    acknowledged?: boolean;
    limit?: number;
  } = {}): Promise<Event[]> {
    const query = new URLSearchParams();
    if (params.device_id) query.append('device_id', params.device_id);
    if (params.type) query.append('type', params.type);
    if (params.severity) query.append('severity', params.severity);
    if (params.acknowledged !== undefined) query.append('acknowledged', params.acknowledged.toString());
    if (params.limit) query.append('limit', params.limit.toString());

    return this.request<Event[]>(`/events?${query}`);
  }

  async acknowledgeEvent(eventId: string, acknowledgedBy: string): Promise<Event> {
    return this.request<Event>(`/events/${eventId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    });
  }
}

export const apiClient = new APIClient(API_BASE_URL);
