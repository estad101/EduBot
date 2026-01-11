"""Notification API endpoints for users and admins."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db, get_db_sync, ASYNC_MODE
from models.notification import NotificationType, NotificationPriority
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Use sync database dependency
db_dependency = get_db_sync if ASYNC_MODE else get_db

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def get_notifications(
    phone_number: str,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    db: Session = Depends(db_dependency)
):
    """
    Get notifications for a user.
    
    Query parameters:
    - phone_number: User's phone number (required)
    - limit: Maximum results (default: 50)
    - offset: Number to skip (default: 0)
    - unread_only: Only unread (default: false)
    - notification_type: Filter by type (optional)
    """
    try:
        notify_type = None
        if notification_type:
            try:
                notify_type = NotificationType[notification_type.upper()]
            except KeyError:
                pass
        
        notifications = NotificationService.get_notifications(
            phone_number=phone_number,
            db=db,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            notification_type=notify_type
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": n.id,
                    "type": n.notification_type.value,
                    "priority": n.priority.value,
                    "title": n.title,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat(),
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                    "related_entity": {
                        "type": n.related_entity_type,
                        "id": n.related_entity_id
                    } if n.related_entity_type else None
                }
                for n in notifications
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(notifications)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return {
            "status": "error",
            "message": f"Error retrieving notifications: {str(e)}"
        }


@router.get("/unread-count")
async def get_unread_count(
    phone_number: str,
    db: Session = Depends(db_dependency)
):
    """Get count of unread notifications."""
    try:
        count = NotificationService.get_unread_count(phone_number, db)
        return {
            "status": "success",
            "data": {
                "phone_number": phone_number,
                "unread_count": count
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return {
            "status": "error",
            "message": f"Error retrieving unread count: {str(e)}"
        }


@router.get("/stats")
async def get_notification_stats(
    phone_number: str,
    db: Session = Depends(db_dependency)
):
    """Get notification statistics."""
    try:
        stats = NotificationService.get_notification_stats(phone_number, db)
        return {
            "status": "success",
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {
            "status": "error",
            "message": f"Error retrieving stats: {str(e)}"
        }


@router.post("/{notification_id}/mark-as-read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(db_dependency)
):
    """Mark a notification as read."""
    try:
        success = NotificationService.mark_as_read(notification_id, db)
        
        if success:
            return {
                "status": "success",
                "message": "Notification marked as read"
            }
        else:
            return {
                "status": "error",
                "message": "Notification not found"
            }
    
    except Exception as e:
        logger.error(f"Error marking as read: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@router.post("/mark-all-as-read")
async def mark_all_as_read(
    phone_number: str,
    db: Session = Depends(db_dependency)
):
    """Mark all notifications as read for a user."""
    try:
        success = NotificationService.mark_all_as_read(phone_number, db)
        
        if success:
            return {
                "status": "success",
                "message": "All notifications marked as read"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to mark notifications as read"
            }
    
    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(db_dependency)
):
    """Delete a notification."""
    try:
        success = NotificationService.delete_notification(notification_id, db)
        
        if success:
            return {
                "status": "success",
                "message": "Notification deleted"
            }
        else:
            return {
                "status": "error",
                "message": "Notification not found"
            }
    
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@router.post("/clear")
async def clear_notifications(
    phone_number: str,
    db: Session = Depends(db_dependency)
):
    """Clear all notifications for a user."""
    try:
        success = NotificationService.clear_notifications(phone_number, db)
        
        if success:
            return {
                "status": "success",
                "message": "All notifications cleared"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to clear notifications"
            }
    
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


# Preferences endpoints

@router.get("/preferences")
async def get_preferences(
    phone_number: str,
    db: Session = Depends(db_dependency)
):
    """Get notification preferences for a user."""
    try:
        prefs = NotificationService.get_preferences(phone_number, db)
        
        if prefs:
            return {
                "status": "success",
                "data": {
                    "phone_number": prefs.phone_number,
                    "homework_submitted": prefs.homework_submitted,
                    "homework_reviewed": prefs.homework_reviewed,
                    "chat_messages": prefs.chat_messages,
                    "subscription_alerts": prefs.subscription_alerts,
                    "account_updates": prefs.account_updates,
                    "system_alerts": prefs.system_alerts,
                    "prefer_whatsapp": prefs.prefer_whatsapp,
                    "prefer_email": prefs.prefer_email,
                    "quiet_hours_enabled": prefs.quiet_hours_enabled,
                    "quiet_hours_start": prefs.quiet_hours_start,
                    "quiet_hours_end": prefs.quiet_hours_end,
                    "batch_notifications": prefs.batch_notifications,
                }
            }
        else:
            return {
                "status": "error",
                "message": "Preferences not found"
            }
    
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@router.post("/preferences")
async def update_preferences(
    phone_number: str,
    request_body: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """
    Update notification preferences.
    
    Request body example:
    {
        "homework_submitted": true,
        "chat_messages": true,
        "prefer_whatsapp": true,
        "prefer_email": false,
        "quiet_hours_enabled": true,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00"
    }
    """
    try:
        prefs = NotificationService.update_preferences(
            phone_number=phone_number,
            db=db,
            **request_body
        )
        
        if prefs:
            return {
                "status": "success",
                "message": "Preferences updated",
                "data": {
                    "phone_number": prefs.phone_number,
                    "homework_submitted": prefs.homework_submitted,
                    "homework_reviewed": prefs.homework_reviewed,
                    "chat_messages": prefs.chat_messages,
                    "subscription_alerts": prefs.subscription_alerts,
                    "account_updates": prefs.account_updates,
                    "system_alerts": prefs.system_alerts,
                    "prefer_whatsapp": prefs.prefer_whatsapp,
                    "prefer_email": prefs.prefer_email,
                    "quiet_hours_enabled": prefs.quiet_hours_enabled,
                    "quiet_hours_start": prefs.quiet_hours_start,
                    "quiet_hours_end": prefs.quiet_hours_end,
                    "batch_notifications": prefs.batch_notifications,
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to update preferences"
            }
    
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }
