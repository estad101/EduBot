"""
Lead model for tracking potential students who have messaged the bot but not registered.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Lead(Base):
    """
    Lead model - tracks potential students from WhatsApp messages.
    
    A lead is created when an unregistered phone number sends a message.
    Once they complete registration, they become a Student.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    sender_name = Column(String(255), nullable=True)
    first_message = Column(Text, nullable=True)
    last_message = Column(Text, nullable=True)
    message_count = Column(Integer, default=1)
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    converted_to_student = Column(Boolean, default=False)
    student_id = Column(Integer, nullable=True, index=True)  # Reference to Student if converted
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    last_message_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Lead(phone={self.phone_number}, name={self.sender_name}, messages={self.message_count})>"
