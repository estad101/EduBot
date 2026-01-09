"""
Support Ticket model - represents chat support requests from students.
"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, Text, Boolean
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from config.database import Base


class TicketStatus(str, enum.Enum):
    """Status of support ticket."""
    OPEN = "OPEN"               # Awaiting admin response
    IN_PROGRESS = "IN_PROGRESS" # Admin has started responding
    RESOLVED = "RESOLVED"       # Issue resolved
    CLOSED = "CLOSED"           # Ticket closed by admin


class TicketPriority(str, enum.Enum):
    """Priority of support ticket."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class SupportTicket(Base):
    """
    Support ticket model for chat support requests.
    
    Fields:
        id: Primary key
        student_id: Foreign key to students table (if student)
        phone_number: Phone number of user requesting support
        sender_name: Name of user requesting support
        issue_description: Initial description of issue
        status: Current ticket status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
        priority: Priority level assigned by admin
        assigned_admin_id: ID of admin handling the ticket
        created_at: When the ticket was created
        updated_at: Last update timestamp
        resolved_at: When the ticket was resolved
    """
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(20), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    issue_description = Column(Text, nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    assigned_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", backref="support_tickets")
    assigned_admin = relationship("User", backref="assigned_tickets", foreign_keys=[assigned_admin_id])
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_phone_number_status", "phone_number", "status"),
        Index("idx_status", "status"),
        Index("idx_assigned_admin", "assigned_admin_id"),
        Index("idx_student_id", "student_id"),
    )

    def __repr__(self):
        return f"<SupportTicket(id={self.id}, phone_number={self.phone_number}, status={self.status})>"


class SupportMessage(Base):
    """
    Messages within a support ticket conversation.
    
    Fields:
        id: Primary key
        ticket_id: Foreign key to support_tickets table
        sender_type: 'user' or 'admin'
        sender_name: Name of sender
        message: Message content
        created_at: When the message was sent
    """
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(10), nullable=False)  # 'user' or 'admin'
    sender_name = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="messages")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_ticket_id_created", "ticket_id", "created_at"),
    )

    def __repr__(self):
        return f"<SupportMessage(id={self.id}, ticket_id={self.ticket_id}, sender={self.sender_type})>"
