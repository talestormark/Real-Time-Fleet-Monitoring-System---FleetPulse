import { Activity, AlertTriangle, Battery, Wifi } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { Device, Event } from '../types';

interface StatsCardsProps {
  devices: Device[];
  events: Event[];
}

export function StatsCards({ devices, events }: StatsCardsProps) {
  const navigate = useNavigate();
  const onlineDevices = devices.filter((d) => d.status === 'online').length;
  const criticalEvents = events.filter((e) => e.severity === 'critical').length;
  const warningEvents = events.filter((e) => e.severity === 'warning').length;
  const totalDevices = devices.length;
  const onlinePercentage = totalDevices > 0 ? Math.round((onlineDevices / totalDevices) * 100) : 0;

  const scrollToFleetOverview = () => {
    const element = document.getElementById('fleet-overview');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleCardClick = (label: string) => {
    if (label === 'Total Devices' || label === 'Online') {
      scrollToFleetOverview();
    } else if (label === 'Critical Events') {
      navigate('/events');
    }
    // Warnings: do nothing for now
  };

  const stats = [
    {
      label: 'Total Devices',
      value: devices.length,
      icon: Activity,
      color: 'blue',
      bgGradient: 'from-blue-500 to-blue-600',
      percentage: null,
    },
    {
      label: 'Online',
      value: onlineDevices,
      icon: Wifi,
      color: 'green',
      bgGradient: 'from-green-500 to-green-600',
      percentage: onlinePercentage,
    },
    {
      label: 'Critical Events',
      value: criticalEvents,
      icon: AlertTriangle,
      color: 'red',
      bgGradient: 'from-red-500 to-red-600',
      percentage: null,
    },
    {
      label: 'Warnings',
      value: warningEvents,
      icon: Battery,
      color: 'yellow',
      bgGradient: 'from-yellow-500 to-yellow-600',
      percentage: null,
    },
  ];

  return (
    <div className="metrics-grid">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const isClickable = stat.label !== 'Warnings';
        return (
          <div
            key={stat.label}
            className={`metric-card ${isClickable ? 'cursor-pointer' : ''}`}
            onClick={() => isClickable && handleCardClick(stat.label)}
          >
            <div className="metric-label">
              <span className="metric-icon">
                <Icon className="h-6 w-6" style={{ color: `var(--${stat.color})` }} />
              </span>
              {stat.label}
            </div>
            <div className="metric-value">{stat.value}</div>
            {stat.percentage !== null && (
              <div className="mt-2 text-sm" style={{ color: '#6b7280' }}>
                {stat.percentage}% of total
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
