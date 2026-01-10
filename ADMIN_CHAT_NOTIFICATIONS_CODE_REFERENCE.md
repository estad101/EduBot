# Admin Chat Notifications - Code Reference

## Summary of Changes

### File 1: services/notification_trigger.py
**Lines Added: ~130 lines**

Three new trigger methods for admin notifications:

```python
@staticmethod
def on_chat_support_initiated_admin(
    phone_number: str,
    user_name: Optional[str] = None,
    admin_phone: str = "admin",
    db: Optional[Session] = None
):
    """Trigger notification to admins when user initiates chat support."""
    # Creates HIGH priority BOTH channel notification
    # Message: "💬 New Chat Support Request\n\nFrom: {user_name}\n..."
    # Related entity: chat_support:{phone_number}

@staticmethod
def on_chat_user_message_admin(
    phone_number: str,
    user_name: Optional[str] = None,
    message_preview: str = "",
    admin_phone: str = "admin",
    db: Optional[Session] = None
):
    """Trigger notification to admins when user sends message in chat."""
    # Creates NORMAL priority IN_APP notification
    # Message: "💬 New Message from User\n\nFrom: {user_name}\nMessage: {preview}..."
    # Related entity: chat_support:{phone_number}

@staticmethod
def on_chat_support_ended_admin(
    phone_number: str,
    user_name: Optional[str] = None,
    admin_phone: str = "admin",
    duration_minutes: Optional[int] = None,
    db: Optional[Session] = None
):
    """Trigger notification to admins when chat support session ends."""
    # Creates NORMAL priority IN_APP notification
    # Message: "↩️ Chat Support Ended\n\nUser: {user_name}\n...Duration: {minutes}..."
    # Related entity: chat_support:{phone_number}
```

### File 2: services/conversation_service.py
**Changes in 3 locations**

**Location 1 - Imports (Line 12-17)**
```python
# Import NotificationTrigger for chat notifications
try:
    from services.notification_trigger import NotificationTrigger
except ImportError:
    NotificationTrigger = None
```

**Location 2 - Method Signature (Line 303-316)**
```python
@staticmethod
def get_next_response(
    phone_number: str, message_text: str, student_data: Optional[Dict] = None, db: Any = None
) -> tuple[str, Optional[ConversationState]]:
    """
    Get the next response based on conversation state and message.

    Args:
        phone_number: User's phone number
        message_text: User's message text
        student_data: Optional student data from database (includes name, status, etc.)
        db: Optional database session for notification triggers  # NEW

    Returns:
        Tuple of (response_message, next_state)
    """
```

**Location 3A - Support Command Handler (Line ~510)**
```python
# Handle chat support command
if intent == "support":
    greeting = f"Hi {first_name}! 💬" if first_name else "💬"
    support_text = (
        f"{greeting}\n\n"
        f"📞 Live Chat Support\n\n"
        # ... support text ...
    )
    
    # Store that user is now in active chat support
    ConversationService.set_data(phone_number, "in_chat_support", True)
    ConversationService.set_data(phone_number, "chat_support_active", True)
    ConversationService.set_data(phone_number, "chat_start_time", datetime.now().isoformat())
    
    # Trigger admin notification [NEW CODE]
    if NotificationTrigger and db:
        try:
            user_name = student_data.get("name") if student_data else "Unknown User"
            NotificationTrigger.on_chat_support_initiated_admin(
                phone_number=phone_number,
                user_name=user_name,
                admin_phone="admin",
                db=db
            )
        except Exception as e:
            logger.warning(f"Could not send admin chat notification: {str(e)}")
    
    return (support_text, ConversationState.CHAT_SUPPORT_ACTIVE)
```

**Location 3B - Chat Message Handler (Line ~330)**
```python
if current_state == ConversationState.CHAT_SUPPORT_ACTIVE and intent != "end_chat":
    # User sent a message during active chat - store it and notify admin
    ConversationService.set_data(phone_number, "chat_support_active", True)
    ConversationService.set_data(phone_number, "chat_last_message_time", datetime.now().isoformat())
    
    # Store the message content for admin review
    chat_messages = ConversationService.get_data(phone_number, "chat_messages") or []
    if isinstance(chat_messages, str):
        chat_messages = []
    chat_messages.append({
        "text": message_text,
        "timestamp": datetime.now().isoformat(),
        "sender": "user"
    })
    ConversationService.set_data(phone_number, "chat_messages", chat_messages)
    
    # Trigger admin notification for user message [NEW CODE]
    if NotificationTrigger and db:
        try:
            user_name = student_data.get("name") if student_data else "Unknown User"
            message_preview = message_text[:100]
            NotificationTrigger.on_chat_user_message_admin(
                phone_number=phone_number,
                user_name=user_name,
                message_preview=message_preview,
                admin_phone="admin",
                db=db
            )
        except Exception as e:
            logger.warning(f"Could not send admin message notification: {str(e)}")
    
    # Acknowledge message to user
    ack_message = (
        "✓ Your message has been sent to support.\n\n"
        "An admin will respond shortly. You can continue typing or select 'End Chat' to exit."
    )
    return (ack_message, ConversationState.CHAT_SUPPORT_ACTIVE)
```

**Location 3C - End Chat Handler (Line ~365)**
```python
# Handle end chat command
if intent == "end_chat":
    try:
        # Close the support ticket if one is open
        ticket_id = ConversationService.get_data(phone_number, "support_ticket_id")
        if ticket_id:
            from services.support_service import SupportService
            from config.database import SessionLocal
            db_temp = SessionLocal()
            try:
                SupportService.update_ticket_status(db_temp, ticket_id, "CLOSED")
            finally:
                db_temp.close()
        
        # Calculate chat duration [NEW CODE]
        duration_minutes = None
        chat_start_time = ConversationService.get_data(phone_number, "chat_start_time")
        if chat_start_time:
            try:
                start_dt = datetime.fromisoformat(chat_start_time)
                duration = datetime.now() - start_dt
                duration_minutes = int(duration.total_seconds() / 60)
            except:
                pass
        
        # Trigger notification that user ended chat [NEW CODE]
        if NotificationTrigger and db:
            try:
                user_name = student_data.get("name") if student_data else "User"
                NotificationTrigger.on_chat_support_ended_admin(
                    phone_number=phone_number,
                    user_name=user_name,
                    admin_phone="admin",
                    duration_minutes=duration_minutes,
                    db=db
                )
            except Exception as e:
                logger.warning(f"Could not send chat ended notification: {str(e)}")
        
        # Clear support data
        ConversationService.set_data(phone_number, "requesting_support", False)
        ConversationService.set_data(phone_number, "support_ticket_id", None)
        ConversationService.set_data(phone_number, "in_chat_support", False)
        ConversationService.set_data(phone_number, "chat_support_active", False)
        ConversationService.set_data(phone_number, "chat_start_time", None)
    except Exception as e:
        logger.warning(f"Could not close support ticket: {str(e)}")
    
    # Return to appropriate state...
```

### File 3: api/routes/whatsapp.py
**1 line changed**

**Location - Message Handler (Line ~145)**
```python
# From:
response_text, next_state = MessageRouter.get_next_response(
    phone_number,
    message_text,
    student_data=student_data,
)

# To:
response_text, next_state = MessageRouter.get_next_response(
    phone_number,
    message_text,
    student_data=student_data,
    db=db  # Added parameter
)
```

### File 4: admin/routes/api.py
**Import added + 2 locations updated**

**Import (Line 20)**
```python
from services.notification_trigger import NotificationTrigger
```

**Location 1 - Send Chat Message Endpoint (~1950)**
```python
if result.get("status") == "success":
    # Store admin message in conversation
    chat_messages = ConversationService.get_data(phone_number, "chat_messages") or []
    if isinstance(chat_messages, str):
        chat_messages = []
    
    chat_messages.append({
        "text": message_text,
        "timestamp": datetime.now().isoformat(),
        "sender": "admin"
    })
    ConversationService.set_data(phone_number, "chat_messages", chat_messages)
    
    # Trigger notification to user for admin message [NEW CODE]
    try:
        student = db.query(Student).filter(Student.phone_number == phone_number).first()
        user_name = student.name if student else "Support Team"
        NotificationTrigger.on_chat_message_received(
            phone_number=phone_number,
            sender_name="Support Team",
            message_preview=message_text[:100],
            db=db
        )
    except Exception as e:
        logger.warning(f"Could not send user chat notification: {str(e)}")
    
    logger.info(f"Admin sent chat support message to {phone_number}")
    
    return {
        "status": "success",
        "message": "Message sent to user",
        # ...
    }
```

**Location 2 - End Chat Endpoint (~2040)**
```python
# Update conversation state
ConversationService.set_data(phone_number, "chat_support_active", False)
ConversationService.set_data(phone_number, "in_chat_support", False)
chat_start_time = ConversationService.get_data(phone_number, "chat_start_time")  # NEW
ConversationService.set_data(phone_number, "chat_messages", None)
ConversationService.set_state(phone_number, ConversationState.IDLE)

# Calculate chat duration [NEW CODE]
duration_minutes = None
if chat_start_time:
    try:
        start_dt = datetime.fromisoformat(chat_start_time)
        duration = datetime.now() - start_dt
        duration_minutes = int(duration.total_seconds() / 60)
    except:
        pass

# Trigger notification that chat has ended [NEW CODE]
try:
    student = db.query(Student).filter(Student.phone_number == phone_number).first()
    user_name = student.name if student else "User"
    NotificationTrigger.on_chat_support_ended_admin(
        phone_number=phone_number,
        user_name=user_name,
        admin_phone="admin",
        duration_minutes=duration_minutes,
        db=db
    )
except Exception as e:
    logger.warning(f"Could not send chat ended notification: {str(e)}")

logger.info(f"Admin ended chat support session with {phone_number}")

return {
    "status": "success",
    "message": "Chat support session ended",
    # ...
}
```

## Integration Points Summary

| Event | Location | Notification Trigger | Admin Receives |
|-------|----------|----------------------|-----------------|
| User types "support" | conversation_service.py:510 | on_chat_support_initiated_admin() | HIGH priority: New chat request |
| User sends message | conversation_service.py:330 | on_chat_user_message_admin() | NORMAL priority: New message preview |
| Admin sends message | admin/routes/api.py:1950 | on_chat_message_received() | User gets notification (existing) |
| User ends chat | conversation_service.py:365 | on_chat_support_ended_admin() | Chat ended notification with duration |
| Admin ends chat | admin/routes/api.py:2040 | on_chat_support_ended_admin() | Chat ended notification with duration |

## Testing Commands

```bash
# 1. Test user initiating chat
# Send WhatsApp message: "support"
# Expected: Admin gets HIGH priority notification

# 2. Test user sending message in chat
# Send WhatsApp message: "I need help with my homework"
# Expected: Admin gets notification with message preview

# 3. Test admin response (via NotificationsPanel)
# Click chat → Click "Send Message" → Type message
# Expected: User gets notification

# 4. Test user ending chat
# Send WhatsApp message: "end chat"
# Expected: Admin gets notification with chat duration

# 5. Test admin ending chat (via NotificationsPanel)
# Click chat → Click "End Chat"
# Expected: Admin notification created, user returned to menu
```

## Monitoring

Check logs for notification triggers:
```
grep "Admin notified: Chat support" application.log
grep "Admin notified: Chat message" application.log
grep "Could not send admin" application.log  # Errors
```

Database queries to verify notifications created:
```sql
SELECT * FROM notifications 
WHERE notification_type IN ('CHAT_SUPPORT_STARTED', 'CHAT_MESSAGE', 'CHAT_SUPPORT_ENDED')
ORDER BY created_at DESC
LIMIT 20;
```

## Rollback

If issues occur, revert these 4 files:
1. services/notification_trigger.py - Remove 3 new methods
2. services/conversation_service.py - Remove NotificationTrigger import and trigger calls (3 locations)
3. api/routes/whatsapp.py - Remove db parameter from get_next_response()
4. admin/routes/api.py - Remove NotificationTrigger import and trigger calls (2 locations)
