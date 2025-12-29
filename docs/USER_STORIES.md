# FleetPulse - User Stories

## Overview
FleetPulse is a real-time fleet monitoring system that provides comprehensive tracking of device status, locations, telemetry data, and critical events for fleet management.

---

## Epic 1: Dashboard & Fleet Overview

### US-1.1: View Fleet Metrics at a Glance
**As a** fleet manager
**I want to** see key fleet metrics (total devices, online devices, critical events, warnings) displayed prominently on the dashboard
**So that** I can quickly assess the overall health and status of my fleet

**Acceptance Criteria:**
- Total devices count is displayed with an Activity icon
- Online devices count is displayed with a Wifi icon and percentage
- Critical events count is displayed with an AlertTriangle icon
- Warnings count is displayed with a Battery icon
- All metrics auto-refresh every 5-10 seconds
- Each metric card has distinct color coding (blue, green, red, yellow)

### US-1.2: Navigate to Fleet Details via Metric Cards
**As a** fleet manager
**I want to** click on metric cards to navigate to relevant sections
**So that** I can quickly drill down into specific fleet information

**Acceptance Criteria:**
- Clicking "Total Devices" card scrolls smoothly to Fleet Overview section
- Clicking "Online" card scrolls smoothly to Fleet Overview section
- Clicking "Critical Events" card navigates to the Events page
- Cards have hover effects indicating they are clickable
- Warnings card is non-interactive (reserved for future functionality)

### US-1.3: View Device Locations on Map
**As a** fleet manager
**I want to** see all my devices plotted on an interactive map
**So that** I can visualize the geographic distribution of my fleet

**Acceptance Criteria:**
- Map displays all devices with their current locations
- Devices are shown with appropriate markers
- Map is interactive (pan, zoom)
- Device selection highlights the corresponding device on the map

### US-1.4: View Fleet Overview Table
**As a** fleet manager
**I want to** see a detailed table of all devices with their status and information
**So that** I can review individual device details systematically

**Acceptance Criteria:**
- Table displays: Device name, Model, City, Status, Last Seen timestamp
- Table is scrollable and responsive
- Devices are sorted by status (online first) and last update time
- Online devices appear at the top
- Within each status group, most recently updated devices appear first
- Clicking a row highlights the device on the map
- Status badges have distinct colors (green for online, yellow for offline)

### US-1.5: Monitor Real-Time Updates
**As a** fleet manager
**I want to** receive automatic updates when device status changes
**So that** I can monitor my fleet without manually refreshing

**Acceptance Criteria:**
- Dashboard displays "LIVE" indicator when WebSocket is connected
- Dashboard displays "OFFLINE" indicator when WebSocket is disconnected
- Device data refreshes every 10 seconds
- Events data refreshes every 5 seconds
- Live indicator has pulsing animation
- Updates happen seamlessly without page reload

---

## Epic 2: Events & Alerts Management

### US-2.1: View All Fleet Events
**As a** fleet manager
**I want to** see all events and alerts from my fleet in one place
**So that** I can stay informed about incidents and anomalies

**Acceptance Criteria:**
- Events page displays all unacknowledged events by default
- Each event shows: Type, Severity, Device, Timestamp, Details
- Events auto-refresh every 5 seconds
- Page displays event count
- Empty state message shown when no events match filters

### US-2.2: Filter Events by Type
**As a** fleet manager
**I want to** filter events by type (LOW_BATTERY, STALE, IMPACT, GEOFENCE)
**So that** I can focus on specific categories of incidents

**Acceptance Criteria:**
- Dropdown shows: All Types, LOW_BATTERY, STALE, IMPACT, GEOFENCE
- Selecting a type filters the event list immediately
- Event count updates to reflect filtered results
- Filter state persists during auto-refresh
- Custom select dropdown with clear visual design

### US-2.3: Filter Events by Severity
**As a** fleet manager
**I want to** filter events by severity level (critical, warning, info)
**So that** I can prioritize my response to incidents

**Acceptance Criteria:**
- Dropdown shows: All Severities, Critical, Warning, Info
- Selecting a severity filters the event list immediately
- Critical events are highlighted with red color
- Warning events are highlighted with yellow color
- Info events are highlighted with blue color
- Filter state persists during auto-refresh

### US-2.4: Toggle Acknowledged Events
**As a** fleet manager
**I want to** hide or show acknowledged events
**So that** I can focus on events that still require attention

**Acceptance Criteria:**
- Checkbox labeled "Show acknowledged" is available
- By default, only unacknowledged events are shown
- Checking the box includes acknowledged events in the view
- Event count updates when toggling the checkbox
- Filter state persists during auto-refresh

### US-2.5: Acknowledge Events
**As a** fleet manager
**I want to** acknowledge events after reviewing them
**So that** I can track which incidents have been addressed

**Acceptance Criteria:**
- Each event has an acknowledge button/action
- Clicking acknowledge marks the event as acknowledged
- Acknowledged events are removed from view (unless "Show acknowledged" is enabled)
- System records who acknowledged the event
- Acknowledgment persists in the database

### US-2.6: Navigate Back to Dashboard
**As a** fleet manager
**I want to** easily navigate back to the Dashboard from the Events page
**So that** I can quickly return to the main overview

**Acceptance Criteria:**
- "Back to Dashboard" button is visible at top of Events page
- Button has left arrow icon for clear indication
- Clicking button navigates to Dashboard page
- Button has hover effect (blue background, text color change)
- Button has smooth slide animation on hover

---

## Epic 3: Navigation & User Interface

### US-3.1: Access Application Branding
**As a** user
**I want to** see clear FleetPulse branding in the navigation
**So that** I know which application I'm using

**Acceptance Criteria:**
- FleetPulse logo displayed on the left side of navigation
- Logo uses gradient color scheme (blue → purple → pink)
- Subtitle "Real-time Fleet Monitoring" displayed below logo
- Logo is responsive (larger on bigger screens)
- Logo text is visually prominent with proper typography

### US-3.2: Monitor Connection Status
**As a** user
**I want to** see the real-time connection status in the navigation
**So that** I know if I'm receiving live updates

**Acceptance Criteria:**
- "LIVE" badge shown when WebSocket is connected
- "OFFLINE" badge shown when WebSocket is disconnected
- LIVE badge has green color with pulsing animation
- OFFLINE badge has red color
- Badge positioned on the right side of navigation
- Badge has glow effect on hover

### US-3.3: Consistent Visual Design
**As a** user
**I want to** experience a consistent and modern visual design
**So that** the application is pleasant and professional to use

**Acceptance Criteria:**
- Navigation uses glassmorphism effect (semi-transparent background with backdrop blur)
- Gradient background overlays for visual depth
- Consistent spacing and padding across all pages
- Responsive design adapts to different screen sizes
- Navigation aligns perfectly with content below
- Premium hover effects and transitions throughout

---

## Epic 4: Device Telemetry & Data

### US-4.1: View Device Information
**As a** fleet manager
**I want to** see detailed information about each device
**So that** I can identify and track individual units

**Acceptance Criteria:**
- Device list shows: Name, ID, Model, Firmware version
- Location information displayed (City)
- Status clearly indicated (online/offline)
- Last seen timestamp shows relative time (e.g., "5 minutes ago")
- Device information updates in real-time

### US-4.2: Monitor Device Health
**As a** fleet manager
**I want to** monitor device health indicators
**So that** I can proactively address issues

**Acceptance Criteria:**
- Online/offline status is clearly visible
- Stale devices (no updates for 15+ minutes) are flagged
- Low battery devices (<20%) trigger LOW_BATTERY events
- Device status badges use color coding (green = online, yellow/red = issues)
- Status updates automatically via WebSocket

---

## Epic 5: System Configuration & Thresholds

### US-5.1: Event Detection Thresholds
**As a** system administrator
**I want to** have configurable thresholds for event detection
**So that** I can tune the system to my fleet's needs

**Current Configuration:**
- Low battery threshold: 20%
- Stale device threshold: 15 minutes
- Impact detection threshold: 3.0 G-force
- All thresholds configurable via environment variables

### US-5.2: Real-Time Data Processing
**As a** fleet manager
**I want to** have incoming telemetry processed in real-time
**So that** I can respond quickly to events

**Acceptance Criteria:**
- Telemetry data ingested via REST API
- Events detected and created automatically based on thresholds
- WebSocket broadcasts updates to connected clients
- Celery workers process background tasks
- Redis pub/sub enables real-time communication

---

## Non-Functional Requirements

### NFR-1: Performance
- Dashboard loads in under 2 seconds
- Real-time updates have less than 1 second latency
- Application handles 100+ concurrent users
- Map renders smoothly with 100+ device markers

### NFR-2: Responsiveness
- Application works on desktop (1024px+)
- Application works on tablets (768px - 1024px)
- Application works on mobile (320px - 768px)
- Navigation and content adapt to screen size
- Touch-friendly controls on mobile devices

### NFR-3: Accessibility
- Keyboard navigation supported
- Clear visual indicators for interactive elements
- Sufficient color contrast for readability
- Hover states provide clear feedback
- Error states are clearly communicated

### NFR-4: Browser Compatibility
- Works on latest Chrome, Firefox, Safari, Edge
- Graceful degradation for older browsers
- WebSocket fallback mechanisms

---

## Future Enhancements

### Potential User Stories for Future Sprints:

1. **US-6.1:** Device Commands - Send commands to devices remotely
2. **US-6.2:** Historical Analytics - View trends and patterns over time
3. **US-6.3:** Geofencing - Create virtual boundaries and alerts
4. **US-6.4:** Custom Dashboards - Create personalized dashboard views
5. **US-6.5:** Export Reports - Generate PDF/CSV reports
6. **US-6.6:** User Management - Multiple user roles and permissions
7. **US-6.7:** Notifications - Email/SMS alerts for critical events
8. **US-6.8:** Device Groups - Organize devices into custom groups
9. **US-6.9:** Maintenance Scheduling - Track maintenance schedules
10. **US-6.10:** Route Optimization - Optimize fleet routing

---

## Technical Stack

**Frontend:**
- React 18 with TypeScript
- TanStack Query (React Query) for data fetching
- React Router for navigation
- Tailwind CSS for styling
- Lucide React for icons
- date-fns for date formatting

**Backend:**
- FastAPI (Python)
- PostgreSQL database
- Redis for caching and pub/sub
- Celery for background tasks
- WebSocket for real-time updates

**Infrastructure:**
- Docker for containerization
- Uvicorn for ASGI server
- Asyncpg for async database operations

---

## Glossary

- **Device**: A GPS-enabled tracking unit in the fleet
- **Telemetry**: Real-time data transmitted from devices (location, battery, speed, etc.)
- **Event**: An incident or anomaly detected from telemetry data
- **Acknowledge**: Mark an event as reviewed/handled
- **Stale Device**: Device that hasn't sent data within the threshold period
- **Geofence**: Virtual geographic boundary for event triggering
- **Impact Event**: Sudden acceleration/deceleration event (potential collision)

---

*Document Version: 1.0*
*Last Updated: December 29, 2024*
*Application: FleetPulse Real-Time Fleet Monitoring*
