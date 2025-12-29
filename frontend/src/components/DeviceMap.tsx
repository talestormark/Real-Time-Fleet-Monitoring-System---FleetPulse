import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Device } from '../types';

// Fix Leaflet's default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface DeviceMapProps {
  devices: Device[];
  selectedDeviceId?: string | null;
  onDeviceSelect?: (deviceId: string) => void;
}

export function DeviceMap({ devices, selectedDeviceId, onDeviceSelect }: DeviceMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Map<string, L.Marker>>(new Map());
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const hasInitializedBounds = useRef(false);

  // Fetch latest telemetry for all devices
  const { data: allTelemetry = [] } = useQuery({
    queryKey: ['all-telemetry', devices.map(d => d.id).join(',')],
    queryFn: async () => {
      if (!devices.length) return [];
      // Fetch latest reading for each device
      const readings = await Promise.all(
        devices.map(async (device) => {
          try {
            const deviceReadings = await apiClient.getTelemetry({ device_id: device.id, limit: 1 });
            return { deviceId: device.id, reading: deviceReadings[0] || null };
          } catch (error) {
            console.error(`Failed to fetch telemetry for ${device.id}:`, error);
            return { deviceId: device.id, reading: null };
          }
        })
      );
      return readings;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
    enabled: devices.length > 0,
  });

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    try {
      const map = L.map(mapContainerRef.current).setView([40.7128, -74.0060], 11);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
      console.log('Map initialized successfully');
    } catch (error) {
      console.error('Failed to initialize map:', error);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Update markers when devices or telemetry changes
  useEffect(() => {
    if (!mapRef.current || !allTelemetry.length) return;

    const map = mapRef.current;
    const newMarkers = new Map<string, L.Marker>();
    const telemetryMap = new Map(allTelemetry.map((t) => [t.deviceId, t.reading]));

    devices.forEach((device) => {
      const latestReading = telemetryMap.get(device.id);
      if (!latestReading?.lat || !latestReading?.lon) return;

      // Reuse existing marker or create new one
      let marker = markersRef.current.get(device.id);

      if (marker) {
        marker.setLatLng([latestReading.lat, latestReading.lon]);
      } else {
        marker = L.marker([latestReading.lat, latestReading.lon])
          .addTo(map);

        marker.on('click', () => {
          onDeviceSelect?.(device.id);
        });
      }

      // Update popup content
      const statusColor = device.status === 'online' ? 'text-green-600' : 'text-red-600';
      marker.bindPopup(`
        <div style="padding: 8px;">
          <h3 style="font-weight: 600; margin-bottom: 4px;">${device.name}</h3>
          <p style="font-size: 12px; color: #666; margin-bottom: 4px;">${device.model}</p>
          <p style="font-size: 12px; margin-bottom: 2px;">Status: <span style="font-weight: 500; color: ${device.status === 'online' ? '#059669' : '#dc2626'};">${device.status}</span></p>
          ${latestReading.battery_pct !== undefined ? `<p style="font-size: 12px; margin-bottom: 2px;">Battery: ${latestReading.battery_pct}%</p>` : ''}
          ${latestReading.speed_mps !== undefined ? `<p style="font-size: 12px;">Speed: ${(latestReading.speed_mps * 3.6).toFixed(1)} km/h</p>` : ''}
        </div>
      `);

      // Highlight selected device
      if (device.id === selectedDeviceId) {
        marker.setOpacity(1);
        marker.openPopup();
      } else {
        marker.setOpacity(0.7);
      }

      newMarkers.set(device.id, marker);
    });

    // Remove markers for devices that no longer exist
    markersRef.current.forEach((marker, deviceId) => {
      if (!newMarkers.has(deviceId)) {
        marker.remove();
      }
    });

    markersRef.current = newMarkers;

    // Fit bounds to show all markers only on initial load
    if (newMarkers.size > 0 && !hasInitializedBounds.current) {
      const bounds = L.latLngBounds([...newMarkers.values()].map((m) => m.getLatLng()));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
      hasInitializedBounds.current = true;
    }
  }, [devices, allTelemetry, selectedDeviceId, onDeviceSelect]);

  return (
    <div
      ref={mapContainerRef}
      className="h-[500px] w-full rounded-lg border border-gray-200"
      style={{ minHeight: '500px' }}
    />
  );
}
