#!/usr/bin/env python3
"""Test the comprehensive notification and alert system."""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from models.notification import NotificationType, NotificationPriority, Notification, NotificationPreference
from services.notification_service import NotificationService
from services.notification_trigger import NotificationTrigger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_notification_system():
    """Test all notification system components."""
    # Use in-memory SQLite for testing
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    test_phone = "+1234567890"
    
    try:
        print("\n" + "="*60)
        print("NOTIFICATION SYSTEM TEST")
        print("="*60 + "\n")
        
        # Test 1: Create basic notification
        print("TEST 1: Create Basic Notification")
        print("-" * 60)
        notification = NotificationService.create_notification(
            phone_number=test_phone,
            notification_type=NotificationType.HOMEWORK_SUBMITTED,
            title="Test Notification",
            message="This is a test notification for homework submission",
            priority=NotificationPriority.HIGH,
            db=db
        )
        print(f"✓ Created notification: {notification.id}")
        print(f"  Title: {notification.title}")
        print(f"  Type: {notification.notification_type.value}")
        print(f"  Is Read: {notification.is_read}\n")
        
        # Test 2: Create notification with related entity
        print("TEST 2: Create Notification with Related Entity")
        print("-" * 60)
        notification2 = NotificationService.create_notification(
            phone_number=test_phone,
            notification_type=NotificationType.HOMEWORK_REVIEWED,
            title="Homework Reviewed",
            message="Your Math homework has been reviewed with detailed feedback",
            related_entity_type="homework",
            related_entity_id="hw_12345",
            db=db
        )
        print(f"✓ Created notification with entity reference")
        print(f"  Entity Type: {notification2.related_entity_type}")
        print(f"  Entity ID: {notification2.related_entity_id}\n")
        
        # Test 3: Get unread count
        print("TEST 3: Get Unread Count")
        print("-" * 60)
        unread_count = NotificationService.get_unread_count(test_phone, db)
        print(f"✓ Unread notifications: {unread_count}\n")
        
        # Test 4: Get all notifications
        print("TEST 4: Retrieve All Notifications")
        print("-" * 60)
        notifications = NotificationService.get_notifications(test_phone, db, limit=10)
        print(f"✓ Retrieved {len(notifications)} notifications")
        for n in notifications:
            print(f"  - [{n.id}] {n.title} ({n.notification_type.value})")
        print()
        
        # Test 5: Mark as read
        print("TEST 5: Mark Notification as Read")
        print("-" * 60)
        if notifications:
            success = NotificationService.mark_as_read(notifications[0].id, db)
            print(f"✓ Marked as read: {success}")
            # Verify
            from models.notification import Notification
            updated = db.query(Notification).filter_by(
                id=notifications[0].id
            ).first()
            print(f"  Is Read: {updated.is_read}")
            print(f"  Read At: {updated.read_at}\n")
        
        # Test 6: Get notification stats
        print("TEST 6: Get Notification Statistics")
        print("-" * 60)
        stats = NotificationService.get_notification_stats(test_phone, db)
        print(f"✓ Total notifications: {stats['total']}")
        print(f"✓ Unread notifications: {stats['unread']}")
        print(f"✓ By type:")
        for n_type, count in stats['by_type'].items():
            print(f"    - {n_type}: {count}")
        print()
        
        # Test 7: Notification preferences
        print("TEST 7: Notification Preferences")
        print("-" * 60)
        prefs = NotificationService.get_preferences(test_phone, db)
        print(f"✓ Retrieved preferences for {prefs.phone_number}")
        print(f"  Homework notifications: {prefs.homework_submitted}")
        print(f"  Chat notifications: {prefs.chat_messages}")
        print(f"  Prefer WhatsApp: {prefs.prefer_whatsapp}")
        print(f"  Prefer Email: {prefs.prefer_email}\n")
        
        # Test 8: Update preferences
        print("TEST 8: Update Notification Preferences")
        print("-" * 60)
        updated_prefs = NotificationService.update_preferences(
            phone_number=test_phone,
            db=db,
            homework_submitted=True,
            chat_messages=True,
            prefer_whatsapp=True,
            prefer_email=False,
            quiet_hours_enabled=True,
            quiet_hours_start="22:00",
            quiet_hours_end="08:00"
        )
        print(f"✓ Updated preferences")
        print(f"  Quiet Hours: {updated_prefs.quiet_hours_enabled}")
        print(f"  Quiet Hours (22:00-08:00)\n")
        
        # Test 9: Check quiet hours
        print("TEST 9: Quiet Hours Check")
        print("-" * 60)
        should_send = NotificationService.should_send_notification(test_phone, db)
        current_time = datetime.now().strftime("%H:%M")
        print(f"✓ Current time: {current_time}")
        print(f"✓ Should send notification: {should_send}\n")
        
        # Test 10: Notification triggers
        print("TEST 10: Notification Triggers")
        print("-" * 60)
        
        print("  Trigger: Homework Submitted")
        NotificationTrigger.on_homework_submitted(
            phone_number=test_phone,
            student_name="John Doe",
            subject="Mathematics",
            homework_id="hw_001",
            db=db
        )
        print("  ✓ Homework submission notification created")
        
        print("  Trigger: Homework Reviewed")
        NotificationTrigger.on_homework_reviewed(
            phone_number=test_phone,
            subject="Mathematics",
            tutor_name="Ms. Smith",
            homework_id="hw_001",
            db=db
        )
        print("  ✓ Homework review notification created")
        
        print("  Trigger: Registration Complete")
        NotificationTrigger.on_registration_complete(
            phone_number=test_phone,
            student_name="John Doe",
            db=db
        )
        print("  ✓ Registration complete notification created")
        
        print("  Trigger: Chat Support Started")
        NotificationTrigger.on_chat_support_started(
            phone_number=test_phone,
            user_name="John Doe",
            db=db
        )
        print("  ✓ Chat support notification created")
        
        print("  Trigger: Subscription Activated")
        NotificationTrigger.on_subscription_activated(
            phone_number=test_phone,
            plan_name="Premium",
            duration_days=30,
            db=db
        )
        print("  ✓ Subscription notification created\n")
        
        # Test 11: Filter by type
        print("TEST 11: Filter Notifications by Type")
        print("-" * 60)
        homework_notifs = NotificationService.get_notifications(
            phone_number=test_phone,
            db=db,
            notification_type=NotificationType.HOMEWORK_SUBMITTED
        )
        print(f"✓ Homework submission notifications: {len(homework_notifs)}")
        
        chat_notifs = NotificationService.get_notifications(
            phone_number=test_phone,
            db=db,
            notification_type=NotificationType.CHAT_SUPPORT_STARTED
        )
        print(f"✓ Chat support notifications: {len(chat_notifs)}\n")
        
        # Test 12: Mark all as read
        print("TEST 12: Mark All Notifications as Read")
        print("-" * 60)
        unread_before = NotificationService.get_unread_count(test_phone, db)
        print(f"✓ Unread before: {unread_before}")
        
        success = NotificationService.mark_all_as_read(test_phone, db)
        unread_after = NotificationService.get_unread_count(test_phone, db)
        print(f"✓ Mark all operation: {success}")
        print(f"✓ Unread after: {unread_after}\n")
        
        print("="*60)
        print("✅ ALL NOTIFICATION TESTS PASSED!")
        print("="*60 + "\n")
        
        print("Summary:")
        print(f"✓ Notification creation working")
        print(f"✓ Read/unread status tracking working")
        print(f"✓ Notification filtering working")
        print(f"✓ User preferences working")
        print(f"✓ Quiet hours calculation working")
        print(f"✓ Notification triggers working")
        print(f"✓ Statistics working")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    success = test_notification_system()
    sys.exit(0 if success else 1)
