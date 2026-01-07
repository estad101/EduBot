"""
Tutor model - represents tutors in the system.
"""
from sqlalchemy import Column, String, DateTime, Index, JSON, Boolean
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class Tutor(Base):
    """
    Tutor model.
    
    Fields:
        id: Primary key
        full_name: Tutor's full name
        email: Email address
        phone_number: WhatsApp phone number
        subjects: JSON array of subject specializations
        bio: Short biography
        is_active: Whether tutor is actively available
        created_at: Registration timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "tutors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    subjects = Column(JSON, nullable=False, default=list)  # ["Mathematics", "English", "Science"]
    bio = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignments = relationship("TutorAssignment", back_populates="tutor", cascade="all, delete-orphan")
    solutions = relationship("TutorSolution", back_populates="tutor", cascade="all, delete-orphan")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_email", "email"),
        Index("idx_phone", "phone_number"),
        Index("idx_is_active", "is_active"),
    )

    def __repr__(self):
        return f"<Tutor(id={self.id}, name={self.full_name}, email={self.email})>"

    def has_subject(self, subject: str) -> bool:
        """Check if tutor specializes in subject."""
        if not self.subjects:
            return False
        return subject.lower() in [s.lower() for s in self.subjects]
