"""
Payment model - represents payment transactions.
"""
from sqlalchemy import Column, String, DateTime, Enum, Index, Numeric, ForeignKey
from sqlalchemy.types import Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Payment(Base):
    """
    Payment transaction model.
    
    Fields:
        id: Primary key
        student_id: Foreign key to students table
        amount: Payment amount (in kobo for Paystack)
        currency: Currency (NGN)
        status: Payment status
        payment_reference: Paystack reference ID (unique)
        authorization_url: Paystack payment URL
        access_code: Paystack access code
        payment_method: Payment method (paystack, etc.)
        idempotency_key: For preventing duplicate processing
        is_subscription: Whether this is for subscription
        webhook_processed: Flag to prevent duplicate webhook processing
        created_at: Payment creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="NGN", nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_reference = Column(String(255), unique=True, nullable=False, index=True)
    authorization_url = Column(String(500), nullable=True)
    access_code = Column(String(255), nullable=True)
    payment_method = Column(String(100), default="paystack", nullable=False)
    idempotency_key = Column(String(255), unique=True, nullable=True)
    is_subscription = Column(Boolean, default=False, nullable=False)
    webhook_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("Student", backref="payments")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_student_reference", "student_id", "payment_reference"),
        Index("idx_status_created", "status", "created_at"),
        Index("idx_webhook_processed", "webhook_processed"),
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, reference={self.payment_reference}, status={self.status})>"
