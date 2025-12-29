import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useCallback } from 'react';
import { Dashboard } from './pages/Dashboard';
import { Events } from './pages/Events';
import { Navigation } from './components/Navigation';
import { useWebSocket } from './hooks/useWebSocket';
import type { WebSocketMessage } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  // WebSocket connection for real-time updates
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    console.log('WebSocket message:', message);

    // Invalidate queries on relevant WebSocket messages
    if (message.type === 'telemetry_update' || message.type === 'device_status_updated') {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      queryClient.invalidateQueries({ queryKey: ['all-telemetry'] });
    }

    if (message.type === 'events_updated' || message.type === 'event_created') {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    }
  }, []);

  const { isConnected } = useWebSocket({
    onMessage: handleWebSocketMessage,
  });

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation isConnected={isConnected} />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/events" element={<Events />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
