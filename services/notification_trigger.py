"""Notification triggers for key bot events."""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from models.notification import NotificationType, NotificationPriority, NotificationChannel
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class NotificationTrigger:
    """Handle notification triggers for various bot events."""
    
    @staticmethod
    def on_homework_submitted(
        phone_number: str,
        student_name: str,
        subject: str,
        homework_id: str,
        db: Session
    ):
        """Trigger when student submits homework."""
        try:
            # Notify admins (would need admin list)
            # For now, create a notification that admins can see
            message = f"📝 New homework submission from {student_name}\n\n"
            message += f"Subject: {subject}\n"
            message += f"ID: {homework_id}"
            
            # This would be sent to admin dashboard
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.HOMEWORK_SUBMITTED,
                title="Homework Submitted",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.IN_APP,
                data={
                    "student_name": student_name,
                    "subject": subject
                },
                related_entity_type="homework",
                related_entity_id=homework_id,
                db=db
            )
            
            logger.info(f"Notified: Homework submitted by {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering homework_submitted notification: {str(e)}")
    
    @staticmethod
    def on_homework_reviewed(
        phone_number: str,
        subject: str,
        tutor_name: Optional[str] = None,
        homework_id: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """Trigger when admin reviews homework."""
        try:
            message = f"✅ Your {subject} homework has been reviewed!\n\n"
            if tutor_name:
                message += f"Reviewed by: {tutor_name}\n"
            message += "Check the app for detailed feedback."
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.HOMEWORK_REVIEWED,
                title="Homework Reviewed",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.WHATSAPP,
                data={
                    "subject": subject,
                    "tutor": tutor_name
                },
                related_entity_type="homework",
                related_entity_id=homework_id,
                db=db
            )
            
            logger.info(f"Notified: Homework reviewed for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering homework_reviewed notification: {str(e)}")
    
    @staticmethod
    def on_chat_support_started(
        phone_number: str,
        user_name: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """Trigger when user initiates chat support."""
        try:
            message = "💬 Chat support session started.\n\n"
            message += "An admin will be with you shortly."
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.CHAT_SUPPORT_STARTED,
                title="Chat Support Connected",
                message=message,
                priority=NotificationPriority.NORMAL,
                channel=NotificationChannel.IN_APP,
                db=db
            )
            
            logger.info(f"Notified: Chat support started for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering chat_support_started notification: {str(e)}")
    
    @staticmethod
    def on_chat_message_received(
        phone_number: str,
        sender_name: str,
        message_preview: str,
        db: Optional[Session] = None
    ):
        """Trigger when new chat message received."""
        try:
            message = f"💬 New message from {sender_name}\n\n"
            message += message_preview[:100]  # First 100 chars
            if len(message_preview) > 100:
                message += "..."
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.CHAT_MESSAGE,
                title="New Chat Message",
                message=message,
                priority=NotificationPriority.NORMAL,
                channel=NotificationChannel.WHATSAPP,
                db=db
            )
            
            logger.info(f"Notified: Chat message for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering chat_message notification: {str(e)}")
    
    @staticmethod
    def on_registration_complete(
        phone_number: str,
        student_name: str,
        db: Optional[Session] = None
    ):
        """Trigger when user completes registration."""
        try:
            message = f"👋 Welcome {student_name}!\n\n"
            message += "Your account is now active.\n"
            message += "You can now submit homework and access all features."
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.REGISTRATION_COMPLETE,
                title="Registration Complete",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.WHATSAPP,
                data={"student_name": student_name},
                db=db
            )
            
            logger.info(f"Notified: Registration complete for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering registration_complete notification: {str(e)}")
    
    @staticmethod
    def on_subscription_activated(
        phone_number: str,
        plan_name: str,
        duration_days: Optional[int] = None,
        db: Optional[Session] = None
    ):
        """Trigger when user activates subscription."""
        try:
            message = f"🎉 Subscription Activated!\n\n"
            message += f"Plan: {plan_name}\n"
            if duration_days:
                message += f"Duration: {duration_days} days\n"
            message += "\nYou now have unlimited homework submissions!"
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.SUBSCRIPTION_ACTIVATED,
                title="Subscription Active",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.BOTH,
                data={
                    "plan": plan_name,
                    "days": duration_days
                },
                db=db
            )
            
            logger.info(f"Notified: Subscription activated for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering subscription_activated notification: {str(e)}")
    
    @staticmethod
    def on_subscription_expiring(
        phone_number: str,
        expiration_date: str,
        days_remaining: int,
        db: Optional[Session] = None
    ):
        """Trigger when subscription is about to expire."""
        try:
            message = f"⏰ Subscription Expiring Soon\n\n"
            message += f"Days remaining: {days_remaining}\n"
            message += f"Expires: {expiration_date}\n\n"
            message += "Renew now to avoid interruption!"
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.SUBSCRIPTION_EXPIRING,
                title="Subscription Expiring",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.WHATSAPP,
                data={
                    "expiration": expiration_date,
                    "days": days_remaining
                },
                db=db
            )
            
            logger.info(f"Notified: Subscription expiring for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering subscription_expiring notification: {str(e)}")
    
    @staticmethod
    def on_payment_confirmed(
        phone_number: str,
        amount: float,
        transaction_id: str,
        db: Optional[Session] = None
    ):
        """Trigger when payment is confirmed."""
        try:
            message = f"✅ Payment Confirmed\n\n"
            message += f"Amount: ${amount:.2f}\n"
            message += f"Transaction ID: {transaction_id}\n\n"
            message += "Thank you for your purchase!"
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.PAYMENT_CONFIRMED,
                title="Payment Received",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.BOTH,
                data={
                    "amount": amount,
                    "transaction_id": transaction_id
                },
                db=db
            )
            
            logger.info(f"Notified: Payment confirmed for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering payment_confirmed notification: {str(e)}")
    
    @staticmethod
    def on_account_updated(
        phone_number: str,
        update_type: str,  # name, email, class, etc.
        db: Optional[Session] = None
    ):
        """Trigger when account is updated."""
        try:
            message = f"📝 Account Updated\n\n"
            message += f"Updated: {update_type.replace('_', ' ').title()}\n\n"
            message += "Your changes have been saved."
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.ACCOUNT_UPDATED,
                title="Account Updated",
                message=message,
                priority=NotificationPriority.NORMAL,
                channel=NotificationChannel.IN_APP,
                data={"update_type": update_type},
                db=db
            )
            
            logger.info(f"Notified: Account updated for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering account_updated notification: {str(e)}")
    
    @staticmethod
    def on_system_alert(
        phone_number: str,
        alert_message: str,
        alert_type: str = "info",  # info, warning, error
        db: Optional[Session] = None
    ):
        """Trigger system alert notification."""
        try:
            priority_map = {
                "info": NotificationPriority.NORMAL,
                "warning": NotificationPriority.HIGH,
                "error": NotificationPriority.URGENT
            }
            
            NotificationService.create_notification(
                phone_number=phone_number,
                notification_type=NotificationType.SYSTEM_ALERT,
                title="System Alert",
                message=alert_message,
                priority=priority_map.get(alert_type, NotificationPriority.NORMAL),
                channel=NotificationChannel.IN_APP,
                data={"alert_type": alert_type},
                db=db
            )
            
            logger.info(f"Notified: System alert for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering system_alert notification: {str(e)}")
    
    @staticmethod
    def on_chat_support_initiated_admin(
        phone_number: str,
        user_name: Optional[str] = None,
        admin_phone: str = "admin",
        db: Optional[Session] = None
    ):
        """Trigger notification to admins when user initiates chat support."""
        try:
            message = f"💬 New Chat Support Request\n\n"
            if user_name:
                message += f"From: {user_name}\n"
            message += f"Phone: {phone_number}\n\n"
            message += "Click to view conversation and respond."
            
            NotificationService.create_notification(
                phone_number=admin_phone,  # Send to admin
                notification_type=NotificationType.CHAT_SUPPORT_STARTED,
                title="New Chat Support Request",
                message=message,
                priority=NotificationPriority.HIGH,
                channel=NotificationChannel.BOTH,  # Notify admin via WhatsApp + In-App
                data={
                    "user_phone": phone_number,
                    "user_name": user_name
                },
                related_entity_type="chat_support",
                related_entity_id=phone_number,
                db=db
            )
            
            logger.info(f"Admin notified: Chat support initiated by {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering admin chat_support notification: {str(e)}")
    
    @staticmethod
    def on_chat_user_message_admin(
        phone_number: str,
        user_name: Optional[str] = None,
        message_preview: str = "",
        admin_phone: str = "admin",
        db: Optional[Session] = None
    ):
        """Trigger notification to admins when user sends message in chat."""
        try:
            message = f"💬 New Message from User\n\n"
            if user_name:
                message += f"From: {user_name}\n"
            message += f"Phone: {phone_number}\n\n"
            message += f"Message: {message_preview[:80]}"
            if len(message_preview) > 80:
                message += "..."
            
            NotificationService.create_notification(
                phone_number=admin_phone,  # Send to admin
                notification_type=NotificationType.CHAT_MESSAGE,
                title="New Chat Message",
                message=message,
                priority=NotificationPriority.NORMAL,
                channel=NotificationChannel.IN_APP,  # In-app for admins
                data={
                    "user_phone": phone_number,
                    "user_name": user_name,
                    "message_preview": message_preview
                },
                related_entity_type="chat_support",
                related_entity_id=phone_number,
                db=db
            )
            
            logger.info(f"Admin notified: Chat message from {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering admin chat_message notification: {str(e)}")
    
    @staticmethod
    def on_chat_support_ended_admin(
        phone_number: str,
        user_name: Optional[str] = None,
        admin_phone: str = "admin",
        duration_minutes: Optional[int] = None,
        db: Optional[Session] = None
    ):
        """Trigger notification to admins when chat support session ends."""
        try:
            message = f"↩️ Chat Support Ended\n\n"
            if user_name:
                message += f"User: {user_name}\n"
            message += f"Phone: {phone_number}\n"
            if duration_minutes:
                message += f"Duration: {duration_minutes} minutes\n"
            message += "\nConversation has been archived."
            
            NotificationService.create_notification(
                phone_number=admin_phone,
                notification_type=NotificationType.CHAT_SUPPORT_ENDED,
                title="Chat Support Ended",
                message=message,
                priority=NotificationPriority.NORMAL,
                channel=NotificationChannel.IN_APP,
                data={
                    "user_phone": phone_number,
                    "user_name": user_name,
                    "duration": duration_minutes
                },
                related_entity_type="chat_support",
                related_entity_id=phone_number,
                db=db
            )
            
            logger.info(f"Admin notified: Chat support ended with {phone_number}")
            
        except Exception as e:
            logger.error(f"Error triggering admin chat_support_ended notification: {str(e)}")

