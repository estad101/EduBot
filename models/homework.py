"""
Homework model - represents student homework submissions.
"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, Text, Boolean
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class SubmissionType(str, enum.Enum):
    """Homework submission type."""
    TEXT = "TEXT"
    IMAGE = "IMAGE"


class PaymentType(str, enum.Enum):
    """Payment type for homework submission."""
    ONE_TIME = "ONE_TIME"
    SUBSCRIPTION = "SUBSCRIPTION"


class HomeworkStatus(str, enum.Enum):
    """Status of homework submission."""
    PENDING = "PENDING"           # Submitted, awaiting payment/tutor
    PAID = "PAID"                 # Payment received
    ASSIGNED = "ASSIGNED"         # Assigned to tutor
    IN_PROGRESS = "IN_PROGRESS"   # Tutor working on solution
    SOLVED = "SOLVED"             # Solution provided to student
    CANCELLED = "CANCELLED"       # Submission cancelled


class Homework(Base):
    """
    Homework submission model.
    
    Fields:
        id: Primary key
        student_id: Foreign key to students table
        subject: Subject/topic of homework
        submission_type: TEXT or IMAGE
        content: Text content (if TEXT submission)
        file_path: Path to uploaded file (if IMAGE submission)
        payment_type: One-time or subscription-based
        payment_id: Reference to payment table (for one-time)
        status: Current status of homework (PENDING, PAID, ASSIGNED, SOLVED)
        assigned_tutor_id: Foreign key to tutors table (tutor assigned to solve)
        created_at: Submission timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    # Allow NULL for student_id - database CASCADE delete will handle removal
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    subject = Column(String(255), nullable=False)
    submission_type = Column(Enum(SubmissionType), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(HomeworkStatus), default=HomeworkStatus.PENDING, nullable=False)
    assigned_tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("Student", backref="homeworks")
    payment = relationship("Payment", backref="homeworks")
    assigned_tutor = relationship("Tutor", backref="assigned_homeworks")
    assignments = relationship("TutorAssignment", back_populates="homework", cascade="all, delete-orphan")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_student_id_created", "student_id", "created_at"),
        Index("idx_payment_type", "payment_type"),
        Index("idx_status", "status"),
        Index("idx_assigned_tutor", "assigned_tutor_id"),
    )

    def __repr__(self):
        return f"<Homework(id={self.id}, student_id={self.student_id}, subject={self.subject})>"
