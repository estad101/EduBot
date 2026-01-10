"""Notification model for tracking alerts and messages."""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from config.database import Base


class NotificationType(str, Enum):
    """Types of notifications in the system."""
    
    HOMEWORK_SUBMITTED = "homework_submitted"  # Student submitted homework
    HOMEWORK_REVIEWED = "homework_reviewed"  # Admin reviewed homework
    CHAT_MESSAGE = "chat_message"  # New chat support message
    CHAT_SUPPORT_STARTED = "chat_support_started"  # User initiated chat support
    CHAT_SUPPORT_ENDED = "chat_support_ended"  # Chat support session ended
    REGISTRATION_COMPLETE = "registration_complete"  # Account registration complete
    SUBSCRIPTION_ACTIVATED = "subscription_activated"  # Subscription purchased
    SUBSCRIPTION_EXPIRING = "subscription_expiring"  # Subscription about to expire
    PAYMENT_CONFIRMED = "payment_confirmed"  # Payment processed
    ACCOUNT_UPDATED = "account_updated"  # Profile information changed
    SYSTEM_ALERT = "system_alert"  # General system notification


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(str, Enum):
    """Channels through which notifications are sent."""
    
    WHATSAPP = "whatsapp"  # WhatsApp message
    EMAIL = "email"  # Email notification
    IN_APP = "in_app"  # Dashboard/UI notification
    BOTH = "both"  # Both WhatsApp and in-app


class Notification(Base):
    """Store notification history and status."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient information
    phone_number = Column(String(20), nullable=False, index=True)
    recipient_type = Column(String(20), default="user")  # user, admin, system
    
    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    channel = Column(SQLEnum(NotificationChannel), default=NotificationChannel.IN_APP)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON data (action references, etc.)
    
    # Status tracking
    is_read = Column(Boolean, default=False, index=True)
    is_sent = Column(Boolean, default=False)  # Whether notification was sent
    send_attempts = Column(Integer, default=0)
    
    # Related entity (homework_id, chat_id, etc.)
    related_entity_type = Column(String(50), nullable=True)  # homework, chat_support, etc.
    related_entity_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.notification_type} to {self.phone_number}>"


class NotificationPreference(Base):
    """Store user notification preferences."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, unique=True, index=True)
    
    # Which notification types are enabled
    homework_submitted = Column(Boolean, default=True)
    homework_reviewed = Column(Boolean, default=True)
    chat_messages = Column(Boolean, default=True)
    subscription_alerts = Column(Boolean, default=True)
    account_updates = Column(Boolean, default=True)
    system_alerts = Column(Boolean, default=True)
    
    # Preferred channels
    prefer_whatsapp = Column(Boolean, default=True)
    prefer_email = Column(Boolean, default=False)
    
    # Quiet hours (no notifications between these times)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)    # HH:MM format
    
    # Notification frequency
    batch_notifications = Column(Boolean, default=False)  # Send in batches instead of immediately
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<NotificationPreference {self.phone_number}>"
