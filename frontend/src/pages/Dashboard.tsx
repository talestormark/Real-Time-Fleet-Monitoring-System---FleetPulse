import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { apiClient } from '../api/client';
import { DeviceMap } from '../components/DeviceMap';
import { DeviceList } from '../components/DeviceList';
import { StatsCards } from '../components/StatsCards';

export function Dashboard() {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);

  // Fetch devices
  const { data: devices = [] } = useQuery({
    queryKey: ['devices'],
    queryFn: () => apiClient.getDevices(),
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // Fetch events for stats only
  const { data: events = [] } = useQuery({
    queryKey: ['events'],
    queryFn: () => apiClient.getEvents({ acknowledged: false, limit: 50 }),
    refetchInterval: 5000,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <StatsCards devices={devices} events={events} />

        {/* Map - Full Width */}
        <section>
          <h2>Device Locations</h2>
          <p className="section-subtitle">Real-time fleet positioning</p>
          <div className="map-container">
            <DeviceMap
              devices={devices}
              selectedDeviceId={selectedDeviceId}
              onDeviceSelect={setSelectedDeviceId}
            />
          </div>
        </section>

        {/* Device List */}
        <section id="fleet-overview">
          <h2>Fleet Overview</h2>
          <p className="section-subtitle">{devices.length} devices in system</p>
          <DeviceList
            devices={devices}
            selectedDeviceId={selectedDeviceId}
            onDeviceSelect={setSelectedDeviceId}
          />
        </section>
      </main>
    </div>
  );
}
