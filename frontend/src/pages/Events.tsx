import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { EventFeed } from '../components/EventFeed';
import { Filter, ArrowLeft } from 'lucide-react';

export function Events() {
  const navigate = useNavigate();
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [showAcknowledged, setShowAcknowledged] = useState(false);

  // Fetch events with filters
  const { data: events = [], refetch: refetchEvents } = useQuery({
    queryKey: ['events', filterType, filterSeverity, showAcknowledged],
    queryFn: () => {
      const params: Record<string, string | number | boolean> = { limit: 100 };
      if (filterType !== 'all') params.type = filterType;
      if (filterSeverity !== 'all') params.severity = filterSeverity;
      if (!showAcknowledged) params.acknowledged = false;
      return apiClient.getEvents(params);
    },
    refetchInterval: 5000,
  });

  const eventTypes = ['all', 'LOW_BATTERY', 'STALE', 'IMPACT', 'GEOFENCE'];
  const severityLevels = ['all', 'critical', 'warning', 'info'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <button
            onClick={() => navigate('/')}
            className="group flex items-center gap-2 px-4 py-2.5 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-blue-50 active:bg-blue-100 font-medium transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
            style={{ marginTop: '0rem', marginBottom: '1.5rem' }}
          >
            <ArrowLeft className="h-5 w-5 transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] group-hover:-translate-x-1" />
            <span>Back to Dashboard</span>
          </button>
          <h2 className="text-3xl font-bold text-gray-900 mb-2 mt-8">Events & Alerts</h2>
          <p className="text-gray-600">
            Monitor and manage fleet incidents in real-time
          </p>
        </div>

        {/* Filters */}
        <div className="filter-card">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-5 w-5 text-purple-600" />
            <h3 className="text-xl font-semibold text-gray-900">Filters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Event Type Filter */}
            <div>
              <label className="form-label">
                Event Type
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="custom-select form-select"
              >
                {eventTypes.map((type) => (
                  <option key={type} value={type}>
                    {type === 'all' ? 'All Types' : type}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Filter */}
            <div>
              <label className="form-label">
                Severity
              </label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="custom-select form-select"
              >
                {severityLevels.map((severity) => (
                  <option key={severity} value={severity}>
                    {severity === 'all' ? 'All Severities' : severity.charAt(0).toUpperCase() + severity.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Show Acknowledged */}
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showAcknowledged}
                  onChange={(e) => setShowAcknowledged(e.target.checked)}
                  className="custom-checkbox"
                />
                <span className="text-sm font-medium text-gray-700">Show acknowledged</span>
              </label>
            </div>

          </div>

          {/* Event Counter */}
          <div className="filter-counter">
            <span className="font-semibold text-gray-900">{events.length}</span>
            <span className="text-gray-600"> events found</span>
          </div>
        </div>

        {/* Events List */}
        <div className="incident-card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 mb-4">
            <h3 className="text-xl font-bold text-gray-900">Active Incidents</h3>
            <p className="text-sm text-gray-500 mt-1">Showing {events.length} events</p>
          </div>
          <div className="px-6 pb-6">
            <EventFeed events={events} onEventUpdate={refetchEvents} />
          </div>
        </div>
      </main>
    </div>
  );
}
