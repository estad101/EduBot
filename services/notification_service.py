"""Notification Service for managing alerts and messages."""

import logging
import json
from datetime import datetime, time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.notification import (
    Notification, 
    NotificationPreference, 
    NotificationType, 
    NotificationPriority,
    NotificationChannel
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating, managing, and sending notifications."""
    
    @staticmethod
    def create_notification(
        phone_number: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        data: Optional[Dict[str, Any]] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Notification:
        """
        Create a new notification.
        
        Args:
            phone_number: Recipient's phone number
            notification_type: Type of notification (from NotificationType enum)
            title: Notification title
            message: Notification message
            priority: Priority level (default: NORMAL)
            channel: Channel to send through (default: IN_APP)
            data: Additional data as dict (will be JSON serialized)
            related_entity_type: Type of related entity (homework, chat_support, etc.)
            related_entity_id: ID of related entity
            db: Database session
        
        Returns:
            Created Notification object
        """
        try:
            # Check user preferences
            if db:
                prefs = NotificationService.get_preferences(phone_number, db)
                
                # Check if this notification type is enabled
                if not NotificationService._is_notification_enabled(notification_type, prefs):
                    logger.debug(f"Notification {notification_type} disabled for {phone_number}")
                    return None
                
                # Determine channel based on preferences
                if prefs:
                    if prefs.prefer_whatsapp and prefs.prefer_email:
                        channel = NotificationChannel.BOTH
                    elif prefs.prefer_whatsapp:
                        channel = NotificationChannel.WHATSAPP
                    elif prefs.prefer_email:
                        channel = NotificationChannel.EMAIL
            
            # Serialize data if provided
            data_str = json.dumps(data) if data else None
            
            # Create notification
            notification = Notification(
                phone_number=phone_number,
                notification_type=notification_type,
                priority=priority,
                channel=channel,
                title=title,
                message=message,
                data=data_str,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                is_read=False,
                is_sent=False
            )
            
            if db:
                db.add(notification)
                db.commit()
                db.refresh(notification)
                logger.info(f"Created notification {notification.id} for {phone_number}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            if db:
                db.rollback()
            return None
    
    @staticmethod
    def _is_notification_enabled(notification_type: NotificationType, prefs: NotificationPreference) -> bool:
        """Check if notification type is enabled in user preferences."""
        if not prefs:
            return True  # Default to enabled if no preferences
        
        type_map = {
            NotificationType.HOMEWORK_SUBMITTED: prefs.homework_submitted,
            NotificationType.HOMEWORK_REVIEWED: prefs.homework_reviewed,
            NotificationType.CHAT_MESSAGE: prefs.chat_messages,
            NotificationType.CHAT_SUPPORT_STARTED: prefs.chat_messages,
            NotificationType.CHAT_SUPPORT_ENDED: prefs.chat_messages,
            NotificationType.SUBSCRIPTION_ACTIVATED: prefs.subscription_alerts,
            NotificationType.SUBSCRIPTION_EXPIRING: prefs.subscription_alerts,
            NotificationType.PAYMENT_CONFIRMED: prefs.subscription_alerts,
            NotificationType.ACCOUNT_UPDATED: prefs.account_updates,
            NotificationType.REGISTRATION_COMPLETE: prefs.account_updates,
            NotificationType.SYSTEM_ALERT: prefs.system_alerts,
        }
        
        return type_map.get(notification_type, True)
    
    @staticmethod
    def get_notifications(
        phone_number: str,
        db: Session,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            phone_number: User's phone number
            db: Database session
            limit: Maximum results to return
            offset: Number of results to skip
            unread_only: Only return unread notifications
            notification_type: Filter by notification type
        
        Returns:
            List of Notification objects
        """
        try:
            query = db.query(Notification).filter(
                Notification.phone_number == phone_number
            ).order_by(Notification.created_at.desc())
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            if notification_type:
                query = query.filter(Notification.notification_type == notification_type)
            
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    @staticmethod
    def get_unread_count(phone_number: str, db: Session) -> int:
        """Get count of unread notifications for a user."""
        try:
            return db.query(Notification).filter(
                Notification.phone_number == phone_number,
                Notification.is_read == False
            ).count()
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0
    
    @staticmethod
    def mark_as_read(notification_id: int, db: Session) -> bool:
        """Mark a notification as read."""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.now()
                db.commit()
                logger.info(f"Marked notification {notification_id} as read")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def mark_all_as_read(phone_number: str, db: Session) -> bool:
        """Mark all notifications for a user as read."""
        try:
            db.query(Notification).filter(
                Notification.phone_number == phone_number,
                Notification.is_read == False
            ).update({
                Notification.is_read: True,
                Notification.read_at: datetime.now()
            })
            db.commit()
            logger.info(f"Marked all notifications as read for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def delete_notification(notification_id: int, db: Session) -> bool:
        """Delete a notification."""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                db.delete(notification)
                db.commit()
                logger.info(f"Deleted notification {notification_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def clear_notifications(phone_number: str, db: Session) -> bool:
        """Clear all notifications for a user."""
        try:
            db.query(Notification).filter(
                Notification.phone_number == phone_number
            ).delete()
            db.commit()
            logger.info(f"Cleared all notifications for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing notifications: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_preferences(phone_number: str, db: Session) -> Optional[NotificationPreference]:
        """Get notification preferences for a user."""
        try:
            prefs = db.query(NotificationPreference).filter(
                NotificationPreference.phone_number == phone_number
            ).first()
            
            # Create default preferences if none exist
            if not prefs:
                prefs = NotificationPreference(phone_number=phone_number)
                db.add(prefs)
                db.commit()
                db.refresh(prefs)
            
            return prefs
            
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            return None
    
    @staticmethod
    def update_preferences(
        phone_number: str,
        db: Session,
        **kwargs
    ) -> Optional[NotificationPreference]:
        """
        Update notification preferences for a user.
        
        Args:
            phone_number: User's phone number
            db: Database session
            **kwargs: Preference fields to update
        
        Returns:
            Updated NotificationPreference object
        """
        try:
            prefs = NotificationService.get_preferences(phone_number, db)
            
            if not prefs:
                prefs = NotificationPreference(phone_number=phone_number)
                db.add(prefs)
            
            # Update allowed fields
            allowed_fields = {
                'homework_submitted', 'homework_reviewed', 'chat_messages',
                'subscription_alerts', 'account_updates', 'system_alerts',
                'prefer_whatsapp', 'prefer_email', 'quiet_hours_enabled',
                'quiet_hours_start', 'quiet_hours_end', 'batch_notifications'
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(prefs, key, value)
            
            prefs.updated_at = datetime.now()
            db.commit()
            db.refresh(prefs)
            logger.info(f"Updated preferences for {phone_number}")
            return prefs
            
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def should_send_notification(
        phone_number: str,
        db: Session
    ) -> bool:
        """
        Check if notification should be sent based on quiet hours.
        
        Args:
            phone_number: User's phone number
            db: Database session
        
        Returns:
            True if notification should be sent, False if in quiet hours
        """
        try:
            prefs = NotificationService.get_preferences(phone_number, db)
            
            if not prefs or not prefs.quiet_hours_enabled:
                return True
            
            if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
                return True
            
            current_time = datetime.now().time()
            start_time = datetime.strptime(prefs.quiet_hours_start, "%H:%M").time()
            end_time = datetime.strptime(prefs.quiet_hours_end, "%H:%M").time()
            
            # Check if current time is within quiet hours
            if start_time <= end_time:
                # Normal case: quiet hours don't cross midnight
                if start_time <= current_time <= end_time:
                    return False
            else:
                # Quiet hours cross midnight
                if current_time >= start_time or current_time <= end_time:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking quiet hours: {str(e)}")
            return True  # Default to sending if error
    
    @staticmethod
    def get_notification_stats(phone_number: str, db: Session) -> Dict[str, Any]:
        """Get notification statistics for a user."""
        try:
            total = db.query(Notification).filter(
                Notification.phone_number == phone_number
            ).count()
            
            unread = db.query(Notification).filter(
                Notification.phone_number == phone_number,
                Notification.is_read == False
            ).count()
            
            by_type = db.query(
                Notification.notification_type,
                func.count(Notification.id)
            ).filter(
                Notification.phone_number == phone_number
            ).group_by(Notification.notification_type).all()
            
            type_counts = {str(n_type): count for n_type, count in by_type}
            
            return {
                "total": total,
                "unread": unread,
                "by_type": type_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            return {"total": 0, "unread": 0, "by_type": {}}
