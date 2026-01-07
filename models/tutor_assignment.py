"""
TutorAssignment and TutorSolution models - track homework assignments and solutions.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text, Enum, Boolean
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class AssignmentStatus(str, enum.Enum):
    """Status of homework assignment."""
    PENDING = "PENDING"           # Waiting for tutor to accept
    ASSIGNED = "ASSIGNED"         # Assigned to tutor
    IN_PROGRESS = "IN_PROGRESS"   # Tutor working on solution
    COMPLETED = "COMPLETED"       # Solution provided
    CANCELLED = "CANCELLED"       # Assignment cancelled


class TutorAssignment(Base):
    """
    Tracks assignment of homework to tutors.
    
    Fields:
        id: Primary key
        homework_id: Foreign key to homeworks table
        tutor_id: Foreign key to tutors table
        status: Assignment status
        assigned_at: When homework was assigned to tutor
        completed_at: When tutor provided solution
    """
    __tablename__ = "tutor_assignments"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id", ondelete="CASCADE"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.PENDING, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    homework = relationship("Homework", back_populates="assignments")
    tutor = relationship("Tutor", back_populates="assignments")
    solution = relationship("TutorSolution", back_populates="assignment", uselist=False, cascade="all, delete-orphan")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_homework_id", "homework_id"),
        Index("idx_tutor_id", "tutor_id"),
        Index("idx_status", "status"),
        Index("idx_assigned_at", "assigned_at"),
    )

    def __repr__(self):
        return f"<TutorAssignment(id={self.id}, homework_id={self.homework_id}, tutor_id={self.tutor_id}, status={self.status})>"


class TutorSolution(Base):
    """
    Tutor solution/response to homework.
    
    Fields:
        id: Primary key
        assignment_id: Foreign key to tutor_assignments table
        tutor_id: Foreign key to tutors table (for quick reference)
        solution_text: Text explanation of solution
        solution_file_path: Path to solution document/image
        is_walkthrough_video: Whether solution includes video walkthrough
        video_url: URL to video walkthrough if applicable
        submitted_at: When solution was submitted
    """
    __tablename__ = "tutor_solutions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("tutor_assignments.id", ondelete="CASCADE"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False)
    solution_text = Column(Text, nullable=True)  # Text explanation
    solution_file_path = Column(String(500), nullable=True)  # Path to image/document
    is_walkthrough_video = Column(Boolean, default=False, nullable=False)
    video_url = Column(String(500), nullable=True)  # URL to video
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignment = relationship("TutorAssignment", back_populates="solution")
    tutor = relationship("Tutor", back_populates="solutions")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_assignment_id", "assignment_id"),
        Index("idx_tutor_id", "tutor_id"),
    )

    def __repr__(self):
        return f"<TutorSolution(id={self.id}, assignment_id={self.assignment_id})>"
