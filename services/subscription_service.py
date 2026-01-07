"""
Subscription service - handles student subscriptions.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.subscription import Subscription
from models.payment import Payment
from models.student import Student, UserStatus
from utils.logger import get_logger

logger = get_logger("subscription_service")


class SubscriptionService:
    """Service for subscription operations."""

    @staticmethod
    def create_subscription(
        db: Session, student_id: int, payment_id: int, amount: str, days: int = 30
    ) -> Subscription:
        """
        Create a new subscription.
        
        Args:
            db: Database session
            student_id: Student ID
            payment_id: Payment ID
            amount: Monthly subscription amount
            days: Subscription duration (default 30)
        
        Returns:
            Created Subscription object
        
        Raises:
            ValueError: If validation fails
        """
        # Check student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Check payment exists and is verified
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        if payment.status.value != "SUCCESS":
            raise ValueError(f"Payment {payment_id} is not verified")

        # Deactivate any existing active subscription
        existing_active = (
            db.query(Subscription)
            .filter(
                Subscription.student_id == student_id,
                Subscription.is_active == True,
            )
            .first()
        )
        if existing_active:
            existing_active.is_active = False
            db.add(existing_active)

        # Create new subscription
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)

        subscription = Subscription(
            student_id=student_id,
            payment_id=payment_id,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            auto_renew=False,
        )

        db.add(subscription)

        # Update student status to ACTIVE_SUBSCRIBER
        student.status = UserStatus.ACTIVE_SUBSCRIBER
        db.add(student)

        db.commit()
        db.refresh(subscription)

        logger.info(
            f"Subscription created: {subscription.id} for student {student_id} "
            f"until {end_date}"
        )

        return subscription

    @staticmethod
    def get_active_subscription(db: Session, student_id: int) -> Optional[Subscription]:
        """
        Get active subscription for student.
        
        Args:
            db: Database session
            student_id: Student ID
        
        Returns:
            Active Subscription or None
        """
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.student_id == student_id,
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow(),
            )
            .first()
        )

        return subscription

    @staticmethod
    def check_subscription_status(db: Session, student_id: int) -> dict:
        """
        Check subscription status for student.
        
        Args:
            db: Database session
            student_id: Student ID
        
        Returns:
            Dictionary with subscription status
        """
        subscription = SubscriptionService.get_active_subscription(db, student_id)

        if not subscription:
            return {
                "has_active_subscription": False,
                "is_expired": None,
                "start_date": None,
                "end_date": None,
                "days_remaining": None,
            }

        days_remaining = (subscription.end_date - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0

        return {
            "has_active_subscription": True,
            "is_expired": subscription.is_expired(),
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "days_remaining": max(0, days_remaining),
        }

    @staticmethod
    def expire_subscription(db: Session, student_id: int) -> bool:
        """
        Expire active subscription for student.
        Revert student status to REGISTERED_FREE.
        
        Args:
            db: Database session
            student_id: Student ID
        
        Returns:
            True if successful
        """
        subscription = SubscriptionService.get_active_subscription(db, student_id)
        if not subscription:
            return False

        subscription.is_active = False
        db.add(subscription)

        # Update student status
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            student.status = UserStatus.REGISTERED_FREE
            db.add(student)

        db.commit()

        logger.info(f"Subscription expired for student {student_id}")
        return True

    @staticmethod
    def get_all_expired_subscriptions(db: Session) -> list[Subscription]:
        """Get all expired subscriptions that are still marked active."""
        return (
            db.query(Subscription)
            .filter(
                Subscription.is_active == True,
                Subscription.end_date <= datetime.utcnow(),
            )
            .all()
        )

    @staticmethod
    def cleanup_expired_subscriptions(db: Session) -> int:
        """
        Mark all expired subscriptions as inactive.
        Called periodically (e.g., by a cron job).
        
        Args:
            db: Database session
        
        Returns:
            Number of subscriptions expired
        """
        expired = SubscriptionService.get_all_expired_subscriptions(db)

        for subscription in expired:
            subscription.is_active = False

            # Update student status
            student = db.query(Student).filter(
                Student.id == subscription.student_id
            ).first()
            if student:
                student.status = UserStatus.REGISTERED_FREE
                db.add(student)

        if expired:
            db.commit()
            logger.info(f"Cleaned up {len(expired)} expired subscriptions")

        return len(expired)
