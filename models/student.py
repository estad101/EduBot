"""
Student model - represents registered students.
"""
from sqlalchemy import Column, String, DateTime, Enum, Index
from sqlalchemy.types import Integer, Boolean
from datetime import datetime
import enum
from config.database import Base


class UserStatus(str, enum.Enum):
    """Student status enumeration."""
    NEW_USER = "NEW_USER"
    REGISTERED_FREE = "REGISTERED_FREE"
    ACTIVE_SUBSCRIBER = "ACTIVE_SUBSCRIBER"


class Student(Base):
    """
    Student model.
    
    Fields:
        id: Primary key
        phone_number: WhatsApp phone number (unique identifier)
        full_name: Student's full name
        email: Email address
        class_grade: Class/grade level
        status: Current user status
        is_active: Account active flag
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    class_grade = Column(String(100), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.REGISTERED_FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Index for faster phone number lookups
    __table_args__ = (
        Index("idx_phone_number", "phone_number"),
        Index("idx_status", "status"),
    )

    def __repr__(self):
        return f"<Student(id={self.id}, phone_number={self.phone_number}, status={self.status})>"
