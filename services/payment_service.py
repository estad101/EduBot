"""
Payment service - handles payment transactions.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.payment import Payment, PaymentStatus
from models.student import Student
from utils.logger import get_logger

logger = get_logger("payment_service")


class PaymentService:
    """Service for payment operations."""

    @staticmethod
    def create_payment(
        db: Session,
        student_id: int,
        amount: float,
        reference: str,
        authorization_url: str,
        access_code: str,
        is_subscription: bool = False,
        idempotency_key: str | None = None,
    ) -> Payment:
        """
        Create a payment record.
        
        Args:
            db: Database session
            student_id: Student ID
            amount: Amount in naira
            reference: Paystack reference
            authorization_url: Paystack checkout URL
            access_code: Paystack access code
            is_subscription: Whether payment is for subscription
            idempotency_key: Key to prevent duplicates
        
        Returns:
            Created Payment object
        
        Raises:
            ValueError: If validation fails
        """
        # Check student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Check if reference already exists
        existing = db.query(Payment).filter(Payment.payment_reference == reference).first()
        if existing:
            raise ValueError(f"Payment with reference {reference} already exists")

        # Create payment
        payment = Payment(
            student_id=student_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            payment_reference=reference,
            authorization_url=authorization_url,
            access_code=access_code,
            is_subscription=is_subscription,
            idempotency_key=idempotency_key,
            webhook_processed=False,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        logger.info(
            f"Payment created: {payment.id} - Student: {student_id}, "
            f"Amount: {amount}, Reference: {reference}"
        )

        return payment

    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Payment | None:
        """Get payment by ID."""
        return db.query(Payment).filter(Payment.id == payment_id).first()

    @staticmethod
    def get_payment_by_reference(db: Session, reference: str) -> Payment | None:
        """Get payment by reference."""
        return db.query(Payment).filter(Payment.payment_reference == reference).first()

    @staticmethod
    def update_payment_status(
        db: Session, payment_id: int, status: PaymentStatus
    ) -> Payment:
        """
        Update payment status.
        
        Args:
            db: Database session
            payment_id: Payment ID
            status: New status
        
        Returns:
            Updated Payment object
        
        Raises:
            ValueError: If payment not found
        """
        payment = PaymentService.get_payment_by_id(db, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        payment.status = status
        db.commit()
        db.refresh(payment)

        logger.info(f"Payment status updated: {payment_id} -> {status.value}")
        return payment

    @staticmethod
    def mark_webhook_processed(db: Session, payment_id: int) -> Payment:
        """
        Mark webhook as processed to prevent duplicates.
        
        Args:
            db: Database session
            payment_id: Payment ID
        
        Returns:
            Updated Payment object
        """
        payment = PaymentService.get_payment_by_id(db, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        payment.webhook_processed = True
        db.commit()
        db.refresh(payment)

        logger.info(f"Webhook marked as processed for payment {payment_id}")
        return payment

    @staticmethod
    def get_student_payments(
        db: Session,
        student_id: int,
        status: PaymentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Payment]:
        """
        Get student's payments.
        
        Args:
            db: Database session
            student_id: Student ID
            status: Filter by status (optional)
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List of Payment objects
        """
        query = db.query(Payment).filter(Payment.student_id == student_id)

        if status:
            query = query.filter(Payment.status == status)

        return query.order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def has_pending_payment(db: Session, student_id: int) -> bool:
        """Check if student has pending payment."""
        return (
            db.query(Payment)
            .filter(
                and_(
                    Payment.student_id == student_id,
                    Payment.status == PaymentStatus.PENDING,
                )
            )
            .first()
        ) is not None

    @staticmethod
    def has_successful_payment(db: Session, student_id: int) -> bool:
        """Check if student has any successful payment."""
        return (
            db.query(Payment)
            .filter(
                and_(
                    Payment.student_id == student_id,
                    Payment.status == PaymentStatus.SUCCESS,
                )
            )
            .first()
        ) is not None
