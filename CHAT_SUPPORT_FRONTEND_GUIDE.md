# 🎨 Chat Support Frontend - Implementation Guide

## Overview

This guide provides the specifications for building the admin dashboard UI components for the chat support feature. All backend endpoints are ready; this document covers the React/Next.js components needed.

---

## Components to Build

### 1. Support Notifications Badge (Header)

**Location**: `admin-ui/components/Navbar.tsx` or `Header.tsx`

**Purpose**: Show count of open support tickets

```tsx
// Component behavior
- Display notification badge in header
- Show: "💬 X open tickets" or just badge number
- Color: Red background if count > 0
- Click to navigate to /support
- API: GET /api/admin/support/notifications (poll every 30s)
- Response: { open_tickets: 5, in_progress: 2, unassigned: 3, has_alerts: true }
```

**Features**:
- Auto-refresh every 30 seconds
- Sound notification on new ticket (optional)
- Shows "New!" badge if has_alerts is true
- Pulsing animation for urgency

---

### 2. Support Tickets List Page

**Location**: `admin-ui/pages/support/index.tsx` or `admin-ui/pages/support.tsx`

**Purpose**: Display all support tickets with filtering

```tsx
// Table columns:
- Phone Number
- Sender Name
- Issue Preview (first 100 chars)
- Status (badge: OPEN/IN_PROGRESS/RESOLVED)
- Priority (badge: LOW/MEDIUM/HIGH/URGENT)
- Message Count (e.g., "5 messages")
- Created Time (relative: "2 hours ago")
- Action: Click row to view detail

// Features:
- Pagination (10-50 tickets per page)
- Sorting by: Created Date, Priority, Status
- Filtering by Status dropdown
- Search by phone number or name
- Real-time updates (poll every 30s)
- Color coding by priority/status
```

**API Call**:
```
GET /api/admin/support/tickets?skip=0&limit=50&status=OPEN

Response:
{
  "tickets": [
    {
      "id": 1,
      "phone_number": "+234...",
      "sender_name": "John Doe",
      "issue_description": "Can't submit homework...",
      "status": "OPEN",
      "priority": "HIGH",
      "message_count": 3,
      "created_at": "2024-01-15T10:30:00",
      "assigned_admin_id": null
    }
  ],
  "total": 25
}
```

---

### 3. Support Ticket Detail Page

**Location**: `admin-ui/pages/support/[id].tsx`

**Purpose**: View ticket details and manage conversation

```tsx
// Layout:
┌─────────────────────────────────────────────────┐
│ Ticket #1 from John Doe                         │
│ Phone: +234...  Status: OPEN  Priority: HIGH    │
├─────────────────────────────────────────────────┤
│                                                 │
│ CONVERSATION THREAD                             │
│                                                 │
│ 10:30 [User] Can't submit homework,fails...    │
│                                                 │
│ 10:45 [Admin] I'll help! What error message?   │
│                                                 │
│ 11:00 [User] It says "File too large"          │
│                                                 │
│ 11:15 [Admin] Try compressing the file first.. │
│                                                 │
│ 11:30 [User] That worked! Thanks so much!      │
│                                                 │
├─────────────────────────────────────────────────┤
│ [Reply text box.............................] │
│ [Send]  [Close Ticket]                         │
└─────────────────────────────────────────────────┘

// Features:
- Chronological message list
- Different styling for user vs admin messages
- Auto-scroll to latest message
- Message timestamps
- Sender labels

// Top panel info:
- Ticket ID and number
- User name and phone
- Current status (badge)
- Priority level
- Created time
- Assignment status
- "Assign to me" button if unassigned
```

**API Calls**:

Get ticket details:
```
GET /api/admin/support/tickets/{id}

Response:
{
  "id": 1,
  "phone_number": "+234...",
  "sender_name": "John Doe",
  "issue_description": "Can't submit homework",
  "status": "OPEN",
  "priority": "HIGH",
  "assigned_admin_id": 5,
  "created_at": "2024-01-15T10:30:00",
  "messages": [
    {
      "id": 1,
      "ticket_id": 1,
      "sender_type": "user",
      "sender_name": "John Doe",
      "message": "Can't submit homework, it fails...",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "ticket_id": 1,
      "sender_type": "admin",
      "sender_name": "Jane Admin",
      "message": "I'll help! What error message?",
      "created_at": "2024-01-15T10:45:00"
    }
  ]
}
```

Send admin response:
```
POST /api/admin/support/tickets/{id}/messages

Body:
{
  "message": "Try compressing the file first..."
}

Response:
{
  "message_id": 3,
  "status": "success",
  "whatsapp_notification_sent": true
}
```

Close ticket:
```
POST /api/admin/support/tickets/{id}/close

Body: (empty or optional close reason)

Response:
{
  "status": "RESOLVED",
  "closed_at": "2024-01-15T12:00:00",
  "user_notification": "sent"
}
```

---

## Data Models (TypeScript)

```typescript
// lib/types/support.ts

interface SupportTicket {
  id: number;
  phone_number: string;
  sender_name: string;
  issue_description: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  message_count?: number;
  assigned_admin_id: number | null;
  student_id?: number | null;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

interface SupportMessage {
  id: number;
  ticket_id: number;
  sender_type: 'user' | 'admin';
  sender_name: string;
  message: string;
  created_at: string;
}

interface SupportNotification {
  open_tickets: number;
  in_progress: number;
  unassigned: number;
  has_alerts: boolean;
}

interface TicketListResponse {
  tickets: SupportTicket[];
  total: number;
  skip: number;
  limit: number;
}
```

---

## API Client Methods

**Location**: `admin-ui/lib/api-client.ts`

Add these methods to existing API client:

```typescript
export const supportApi = {
  // Get notifications for dashboard
  getNotifications: async (): Promise<SupportNotification> => {
    const response = await api.get('/admin/support/notifications');
    return response.data.data;
  },

  // List all tickets with filters
  getTickets: async (
    skip: number = 0,
    limit: number = 50,
    status?: string,
    search?: string
  ): Promise<TicketListResponse> => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    
    const response = await api.get(`/admin/support/tickets?${params}`);
    return response.data.data;
  },

  // Get single ticket with all messages
  getTicket: async (id: number): Promise<{ ticket: SupportTicket; messages: SupportMessage[] }> => {
    const response = await api.get(`/admin/support/tickets/${id}`);
    return response.data.data;
  },

  // Send admin response to user
  sendMessage: async (ticketId: number, message: string): Promise<{ message_id: number }> => {
    const response = await api.post(`/admin/support/tickets/${ticketId}/messages`, {
      message,
    });
    return response.data.data;
  },

  // Close/resolve ticket
  closeTicket: async (ticketId: number): Promise<{ status: string }> => {
    const response = await api.post(`/admin/support/tickets/${ticketId}/close`, {});
    return response.data.data;
  },
};
```

---

## Component Examples

### Support Badge Component

```tsx
import { useEffect, useState } from 'react';
import { supportApi } from '@/lib/api-client';

export default function SupportBadge() {
  const [notifications, setNotifications] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await supportApi.getNotifications();
        setNotifications(data);
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();

    // Poll every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !notifications) return null;

  const { open_tickets, has_alerts } = notifications;

  if (open_tickets === 0) return null;

  return (
    <a href="/support" className={`flex items-center gap-2 px-3 py-1 rounded-full ${
      has_alerts ? 'bg-red-500 animate-pulse' : 'bg-blue-500'
    } text-white text-sm font-semibold`}>
      💬 {open_tickets} {open_tickets === 1 ? 'ticket' : 'tickets'}
    </a>
  );
}
```

### Status Badge Component

```tsx
interface StatusBadgeProps {
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
}

export default function StatusBadge({ status, priority }: StatusBadgeProps) {
  const statusColors = {
    OPEN: 'bg-red-100 text-red-800',
    IN_PROGRESS: 'bg-blue-100 text-blue-800',
    RESOLVED: 'bg-green-100 text-green-800',
    CLOSED: 'bg-gray-100 text-gray-800',
  };

  const priorityColors = {
    LOW: 'bg-gray-100 text-gray-700',
    MEDIUM: 'bg-yellow-100 text-yellow-700',
    HIGH: 'bg-orange-100 text-orange-700',
    URGENT: 'bg-red-100 text-red-700',
  };

  return (
    <div className="flex gap-2">
      <span className={`px-2 py-1 rounded text-xs font-semibold ${statusColors[status]}`}>
        {status}
      </span>
      <span className={`px-2 py-1 rounded text-xs font-semibold ${priorityColors[priority]}`}>
        {priority}
      </span>
    </div>
  );
}
```

---

## Styling Guidelines

### Colors
- **OPEN**: Red (#EF4444) - Requires attention
- **IN_PROGRESS**: Blue (#3B82F6) - Being handled
- **RESOLVED**: Green (#10B981) - Done
- **CLOSED**: Gray (#6B7280) - Archived
- **URGENT**: Red with pulse animation
- **HIGH**: Orange (#F97316)
- **MEDIUM**: Yellow (#EAB308)
- **LOW**: Gray (#9CA3AF)

### Typography
- Ticket list: Regular weight, 14px
- Ticket details: Bold title, 16px
- Messages: 13px, lighter for timestamps
- Badges: 11px, bold

### Layout
- Max width: 1200px (container)
- Padding: 16-24px standard
- Gap between elements: 12-16px
- Message thread: Full width with padding

---

## Navigation Updates

Add to main navigation (e.g., `components/Sidebar.tsx`):

```tsx
<NavLink 
  href="/support"
  icon="💬"
  label="Support Tickets"
  badge={notificationCount > 0 ? notificationCount : null}
  active={pathname === '/support'}
/>
```

---

## Performance Considerations

1. **Pagination**: Load 50 tickets per page (adjust based on speed)
2. **Polling**: 30-second interval for notifications (can use WebSocket for real-time)
3. **Memoization**: Use `useMemo` for message list to prevent re-renders
4. **Virtual List**: Consider `react-window` if >100 messages per ticket
5. **Lazy Loading**: Load messages incrementally if many

---

## Error Handling

```tsx
// Handle API errors
try {
  const data = await supportApi.sendMessage(ticketId, message);
  // Show success toast
} catch (error) {
  if (error.response?.status === 404) {
    // Ticket not found
  } else if (error.response?.status === 403) {
    // Not authorized
  } else {
    // Generic error
    showError('Failed to send message');
  }
}
```

---

## Testing

### Unit Tests
- [ ] Badge shows correct count
- [ ] Status badge colors are correct
- [ ] Sorting/filtering works
- [ ] Pagination buttons work

### Integration Tests
- [ ] Load ticket list
- [ ] Open ticket detail
- [ ] Send message (API call works)
- [ ] Close ticket
- [ ] Notification updates automatically

### Manual Testing
- [ ] Create support ticket via bot
- [ ] Check dashboard notification updates
- [ ] Open ticket detail page
- [ ] View full message history
- [ ] Send admin response
- [ ] Verify WhatsApp notification received
- [ ] Close ticket

---

## Estimated Development Time

- Support badge: 30 minutes
- Tickets list page: 2-3 hours
- Ticket detail page: 3-4 hours
- API client integration: 30 minutes
- Navigation updates: 15 minutes
- Styling & polish: 1-2 hours

**Total: 8-11 hours for experienced React developer**

---

## Quick Start

1. Create folder: `admin-ui/pages/support/`
2. Create files:
   - `index.tsx` (list page)
   - `[id].tsx` (detail page)
3. Create component file: `admin-ui/components/SupportBadge.tsx`
4. Update navigation to include support link
5. Add API client methods to `lib/api-client.ts`
6. Test with actual support tickets from bot

---

## Files Ready

✅ Backend APIs: `/api/support/*` and `/api/admin/support/*`
✅ Database: Tables created with migration
✅ Services: Full business logic implemented
✅ WebSocket support: Can be added for real-time updates
✅ WhatsApp integration: Messages sync automatically

**Ready to build frontend!**
