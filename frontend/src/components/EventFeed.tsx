import { AlertTriangle, Battery, MapPin, Clock, Check } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '../api/client';
import type { Event } from '../types';

interface EventFeedProps {
  events: Event[];
  onEventUpdate: () => void;
}

export function EventFeed({ events, onEventUpdate }: EventFeedProps) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'LOW_BATTERY':
        return <Battery className="h-5 w-5" />;
      case 'IMPACT':
        return <AlertTriangle className="h-5 w-5" />;
      case 'STALE':
        return <Clock className="h-5 w-5" />;
      case 'GEOFENCE':
        return <MapPin className="h-5 w-5" />;
      default:
        return <AlertTriangle className="h-5 w-5" />;
    }
  };

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-900';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-900';
    }
  };

  const getIconColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-500';
      case 'warning':
        return 'text-yellow-500';
      case 'info':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  const handleAcknowledge = async (eventId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.acknowledgeEvent(eventId, 'admin');
      onEventUpdate();
    } catch (error) {
      console.error('Failed to acknowledge event:', error);
    }
  };

  const getEventTitle = (event: Event) => {
    switch (event.type) {
      case 'LOW_BATTERY':
        return `Low Battery: ${event.payload.battery_pct}%`;
      case 'IMPACT':
        return `Impact Detected: ${event.payload.accel_g}G`;
      case 'STALE':
        return `Device Offline`;
      case 'GEOFENCE':
        return `Geofence Violation`;
      default:
        return event.type;
    }
  };

  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Check className="h-12 w-12 mx-auto mb-2 text-green-500" />
        <p>No active events</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[600px] overflow-y-auto">
      {events.map((event) => (
        <div
          key={event.id}
          className={`border rounded-lg p-4 ${getSeverityStyles(event.severity)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className={getIconColor(event.severity)}>
                {getEventIcon(event.type)}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-sm">{getEventTitle(event)}</h4>
                <p className="text-xs text-gray-600 mt-1">{event.device_id}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {formatDistanceToNow(new Date(event.ts), { addSuffix: true })}
                </p>
              </div>
            </div>
            {!event.acknowledged_at && (
              <button
                onClick={(e) => handleAcknowledge(event.id, e)}
                className="text-xs px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              >
                Acknowledge
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
