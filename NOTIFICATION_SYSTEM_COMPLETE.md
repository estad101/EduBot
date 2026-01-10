# Comprehensive Notification & Alert System

## Overview
A complete notification and alert system for EduBot that manages all types of notifications, user preferences, quiet hours, and notification history.

## System Architecture

### 1. **Core Components**

#### Notification Model (`models/notification.py`)
- **Notification Table**: Stores individual notifications with full history
- **NotificationPreference Table**: Stores user preferences for notification types and channels
- **Enums**:
  - `NotificationType`: 11 types of notifications (homework, chat, subscription, etc.)
  - `NotificationPriority`: 4 levels (LOW, NORMAL, HIGH, URGENT)
  - `NotificationChannel`: WhatsApp, Email, In-App, Both

#### Notification Service (`services/notification_service.py`)
Core service with these features:
- Create, retrieve, and manage notifications
- Mark as read/unread
- Delete and clear notifications
- User preference management
- Quiet hours checking
- Statistics generation

#### Notification Triggers (`services/notification_trigger.py`)
Event-based triggers for:
- Homework submission and reviews
- Chat support sessions
- Registration completion
- Subscription events
- Payment confirmation
- Account updates
- System alerts

#### API Routes (`api/routes/notifications.py`)
RESTful endpoints for:
- Retrieve notifications (with filtering and pagination)
- Mark as read operations
- Delete notifications
- Manage preferences
- Get statistics

### 2. **Notification Types**

| Type | Description | Default Priority | Channel |
|------|-------------|------------------|---------|
| HOMEWORK_SUBMITTED | Student submitted homework | HIGH | IN_APP |
| HOMEWORK_REVIEWED | Admin reviewed homework | HIGH | WHATSAPP |
| CHAT_MESSAGE | New chat message | NORMAL | WHATSAPP |
| CHAT_SUPPORT_STARTED | User initiated chat | NORMAL | IN_APP |
| CHAT_SUPPORT_ENDED | Chat session ended | NORMAL | IN_APP |
| REGISTRATION_COMPLETE | Account registered | HIGH | WHATSAPP |
| SUBSCRIPTION_ACTIVATED | Subscription purchased | HIGH | BOTH |
| SUBSCRIPTION_EXPIRING | Subscription about to expire | HIGH | WHATSAPP |
| PAYMENT_CONFIRMED | Payment processed | HIGH | BOTH |
| ACCOUNT_UPDATED | Profile changed | NORMAL | IN_APP |
| SYSTEM_ALERT | General system notification | NORMAL | IN_APP |

### 3. **User Preferences**

Each user can control:

**Notification Types**
- ✓ Homework notifications
- ✓ Chat notifications
- ✓ Subscription alerts
- ✓ Account update notifications
- ✓ System alerts

**Communication Channels**
- ✓ WhatsApp (primary)
- ✓ Email (optional)

**Quiet Hours**
- ✓ Enable/disable
- ✓ Start time (HH:MM)
- ✓ End time (HH:MM)
- ✓ Handles midnight crossing (e.g., 22:00-08:00)

**Notification Batching**
- ✓ Send immediately or batch notifications

## API Endpoints

### Get Notifications
```
GET /api/notifications/?phone_number=+1234567890
Query Parameters:
- phone_number: User's phone (required)
- limit: Results per page (default: 50)
- offset: Page offset (default: 0)
- unread_only: Only unread (default: false)
- notification_type: Filter by type (optional)

Response:
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "type": "homework_submitted",
      "priority": "high",
      "title": "Homework Submitted",
      "message": "New homework...",
      "is_read": false,
      "created_at": "2026-01-10T02:54:55",
      "related_entity": {
        "type": "homework",
        "id": "hw_123"
      }
    }
  ],
  "pagination": {...}
}
```

### Get Unread Count
```
GET /api/notifications/unread-count?phone_number=+1234567890

Response:
{
  "status": "success",
  "data": {
    "phone_number": "+1234567890",
    "unread_count": 3
  }
}
```

### Get Statistics
```
GET /api/notifications/stats?phone_number=+1234567890

Response:
{
  "status": "success",
  "data": {
    "total": 25,
    "unread": 3,
    "by_type": {
      "homework_submitted": 5,
      "chat_message": 2,
      "homework_reviewed": 1,
      ...
    }
  }
}
```

### Mark as Read
```
POST /api/notifications/{notification_id}/mark-as-read

Response:
{
  "status": "success",
  "message": "Notification marked as read"
}
```

### Mark All as Read
```
POST /api/notifications/mark-all-as-read?phone_number=+1234567890

Response:
{
  "status": "success",
  "message": "All notifications marked as read"
}
```

### Delete Notification
```
DELETE /api/notifications/{notification_id}

Response:
{
  "status": "success",
  "message": "Notification deleted"
}
```

### Clear All Notifications
```
POST /api/notifications/clear?phone_number=+1234567890

Response:
{
  "status": "success",
  "message": "All notifications cleared"
}
```

### Get Preferences
```
GET /api/notifications/preferences?phone_number=+1234567890

Response:
{
  "status": "success",
  "data": {
    "phone_number": "+1234567890",
    "homework_submitted": true,
    "homework_reviewed": true,
    "chat_messages": true,
    "subscription_alerts": true,
    "account_updates": true,
    "system_alerts": true,
    "prefer_whatsapp": true,
    "prefer_email": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00",
    "batch_notifications": false
  }
}
```

### Update Preferences
```
POST /api/notifications/preferences?phone_number=+1234567890
Body:
{
  "homework_submitted": true,
  "chat_messages": true,
  "prefer_whatsapp": true,
  "prefer_email": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00"
}

Response:
{
  "status": "success",
  "message": "Preferences updated",
  "data": {...}
}
```

## Integration with Existing Features

### Homework Workflow
```python
# When student submits homework
NotificationTrigger.on_homework_submitted(
    phone_number=student.phone_number,
    student_name=student.name,
    subject=homework.subject,
    homework_id=homework.id,
    db=db
)
```

### Chat Support Workflow
```python
# When user initiates chat
NotificationTrigger.on_chat_support_started(
    phone_number=user.phone_number,
    user_name=user.name,
    db=db
)

# When message received
NotificationTrigger.on_chat_message_received(
    phone_number=user.phone_number,
    sender_name="Admin",
    message_preview=message[:100],
    db=db
)
```

### Registration Workflow
```python
# When registration completes
NotificationTrigger.on_registration_complete(
    phone_number=user.phone_number,
    student_name=user.name,
    db=db
)
```

### Subscription Workflow
```python
# When subscription purchased
NotificationTrigger.on_subscription_activated(
    phone_number=user.phone_number,
    plan_name="Premium",
    duration_days=30,
    db=db
)

# When expiration approaching (scheduled task)
NotificationTrigger.on_subscription_expiring(
    phone_number=user.phone_number,
    expiration_date="2026-02-10",
    days_remaining=7,
    db=db
)
```

## Usage Examples

### Python Service Usage
```python
from services.notification_service import NotificationService
from models.notification import NotificationType, NotificationPriority

# Create notification
notification = NotificationService.create_notification(
    phone_number="+1234567890",
    notification_type=NotificationType.HOMEWORK_REVIEWED,
    title="Homework Reviewed",
    message="Your Math homework has feedback",
    priority=NotificationPriority.HIGH,
    data={"subject": "Math"},
    related_entity_type="homework",
    related_entity_id="hw_123",
    db=db
)

# Get notifications
notifications = NotificationService.get_notifications(
    phone_number="+1234567890",
    db=db,
    unread_only=True,
    limit=20
)

# Update preferences
NotificationService.update_preferences(
    phone_number="+1234567890",
    db=db,
    quiet_hours_enabled=True,
    quiet_hours_start="22:00",
    quiet_hours_end="08:00"
)

# Check if should send notification
should_send = NotificationService.should_send_notification(
    phone_number="+1234567890",
    db=db
)
```

### REST API Usage
```bash
# Get user notifications
curl "http://localhost:8000/api/notifications/?phone_number=%2B1234567890&limit=20"

# Get unread count
curl "http://localhost:8000/api/notifications/unread-count?phone_number=%2B1234567890"

# Mark notification as read
curl -X POST "http://localhost:8000/api/notifications/1/mark-as-read"

# Update preferences
curl -X POST "http://localhost:8000/api/notifications/preferences?phone_number=%2B1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00"
  }'
```

## Features

### ✅ Complete Notification History
- Store all notifications with timestamps
- Related entity tracking (homework ID, chat ID, etc.)
- Read/unread status tracking
- Read timestamp recording

### ✅ Smart Filtering
- Filter by notification type
- Filter by read status
- Pagination support
- Unread count statistics

### ✅ User Preferences
- Enable/disable notification types
- Choose communication channels
- Set quiet hours
- Optional email notifications

### ✅ Quiet Hours
- Enable quiet hours (no notifications during time range)
- Support for midnight-crossing hours (e.g., 22:00-08:00)
- Automatic check before sending

### ✅ Event-Driven
- Automatic triggers on key events
- Homework-related notifications
- Chat support notifications
- Registration and subscription alerts
- Payment confirmations

### ✅ Analytics
- Total notification count
- Unread count
- Breakdown by notification type
- User engagement metrics

## Database Schema

### notifications table
```sql
- id: PRIMARY KEY
- phone_number: INDEX
- notification_type: ENUM, INDEX
- priority: ENUM
- channel: ENUM
- title: VARCHAR(255)
- message: TEXT
- data: JSON (stored as TEXT)
- is_read: BOOLEAN, INDEX
- is_sent: BOOLEAN
- send_attempts: INTEGER
- related_entity_type: VARCHAR(50)
- related_entity_id: VARCHAR(100)
- created_at: DATETIME, INDEX
- read_at: DATETIME
- sent_at: DATETIME
```

### notification_preferences table
```sql
- id: PRIMARY KEY
- phone_number: VARCHAR(20), UNIQUE, INDEX
- homework_submitted: BOOLEAN
- homework_reviewed: BOOLEAN
- chat_messages: BOOLEAN
- subscription_alerts: BOOLEAN
- account_updates: BOOLEAN
- system_alerts: BOOLEAN
- prefer_whatsapp: BOOLEAN
- prefer_email: BOOLEAN
- quiet_hours_enabled: BOOLEAN
- quiet_hours_start: VARCHAR(5) [HH:MM]
- quiet_hours_end: VARCHAR(5) [HH:MM]
- batch_notifications: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
```

## Testing

Run comprehensive notification system test:
```bash
python test_notification_system.py
```

Test coverage:
- ✅ Notification creation
- ✅ Notification retrieval and filtering
- ✅ Read/unread status management
- ✅ User preferences CRUD
- ✅ Quiet hours calculation
- ✅ Event-based triggers
- ✅ Statistics generation
- ✅ Preference updates

## Future Enhancements

- [ ] Email notification sending
- [ ] SMS notifications
- [ ] Push notifications (mobile app)
- [ ] Notification grouping/bundling
- [ ] Custom notification templates
- [ ] Notification scheduling
- [ ] A/B testing for notification content
- [ ] Advanced analytics dashboard
- [ ] Notification retry mechanism
- [ ] Multi-language support

## Files Added

1. `models/notification.py` - Data models
2. `services/notification_service.py` - Core service logic
3. `services/notification_trigger.py` - Event triggers
4. `api/routes/notifications.py` - API endpoints
5. `create_notification_tables.py` - Database initialization
6. `test_notification_system.py` - Comprehensive tests

## Production Checklist

- [ ] Run migrations on production database
- [ ] Integrate triggers into existing workflows
- [ ] Setup email provider for email notifications
- [ ] Configure notification queue for async sending
- [ ] Set up scheduled task for expiration notifications
- [ ] Add notification UI to admin dashboard
- [ ] Add notification preferences UI to user app
- [ ] Monitor notification delivery rates
- [ ] Setup alerting for failed notifications
