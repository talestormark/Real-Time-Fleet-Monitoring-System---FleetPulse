import { Battery, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Device } from '../types';

interface DeviceListProps {
  devices: Device[];
  selectedDeviceId?: string | null;
  onDeviceSelect?: (deviceId: string) => void;
}

export function DeviceList({ devices, selectedDeviceId, onDeviceSelect }: DeviceListProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <Wifi className="h-5 w-5 text-green-500" />;
      case 'offline':
        return <WifiOff className="h-5 w-5 text-gray-400" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return null;
    }
  };

  // Sort devices: online first, then by last update (most recent first)
  const sortedDevices = [...devices].sort((a, b) => {
    // First priority: online status (online comes first)
    const statusOrder = { online: 0, degraded: 1, offline: 2 };
    const statusA = statusOrder[a.status as keyof typeof statusOrder] ?? 3;
    const statusB = statusOrder[b.status as keyof typeof statusOrder] ?? 3;

    if (statusA !== statusB) {
      return statusA - statusB;
    }

    // Second priority: last_seen_at (most recent first)
    const timeA = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
    const timeB = b.last_seen_at ? new Date(b.last_seen_at).getTime() : 0;
    return timeB - timeA; // Descending order (newest first)
  });

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Device
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Model
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              City
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Seen
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedDevices.map((device) => (
            <tr
              key={device.id}
              onClick={() => onDeviceSelect?.(device.id)}
              className={`cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedDeviceId === device.id ? 'bg-blue-50' : ''
              }`}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  {getStatusIcon(device.status)}
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-900">{device.name}</div>
                    <div className="text-sm text-gray-500">{device.id}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{device.model}</div>
                {device.firmware_version && (
                  <div className="text-sm text-gray-500">v{device.firmware_version}</div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{device.city || '-'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`status-badge ${device.status === 'online' ? 'status-online' : 'status-offline'}`}>
                  {device.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {device.last_seen_at
                  ? formatDistanceToNow(new Date(device.last_seen_at), { addSuffix: true })
                  : 'Never'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
