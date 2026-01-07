"""
Subscription model - represents active student subscriptions.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.types import Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from config.database import Base


class Subscription(Base):
    """
    Monthly subscription model.
    
    Fields:
        id: Primary key
        student_id: Foreign key to students table (one active per student)
        payment_id: Link to the initial subscription payment
        amount: Monthly subscription amount (in kobo)
        start_date: Subscription start date
        end_date: Subscription end date (30 days from start)
        is_active: Whether subscription is currently active
        auto_renew: Whether to auto-renew on expiry
        created_at: Subscription creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    amount = Column(String(50), nullable=False)  # Store as string for precision
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    auto_renew = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("Student", backref="subscriptions")
    payment = relationship("Payment", backref="subscription_record")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_student_active", "student_id", "is_active"),
        Index("idx_end_date", "end_date"),
    )

    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        return datetime.utcnow() > self.end_date

    def is_valid(self) -> bool:
        """Check if subscription is valid and active."""
        return self.is_active and not self.is_expired()

    def __repr__(self):
        return f"<Subscription(id={self.id}, student_id={self.student_id}, is_active={self.is_active})>"
