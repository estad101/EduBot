"""
Lead service - handles lead tracking and conversion to students.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models.lead import Lead
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("lead_service")


class LeadService:
    """Service for lead operations."""

    @staticmethod
    def get_or_create_lead(
        db: Session, phone_number: str, sender_name: str = None, first_message: str = None
    ) -> Lead:
        """
        Get existing lead or create a new one.
        
        Args:
            db: Database session
            phone_number: WhatsApp phone number
            sender_name: Name of the person messaging
            first_message: The initial message content
        
        Returns:
            Lead object (created or existing)
        """
        # Check if lead already exists
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        
        if lead:
            # Update last message info
            lead.message_count += 1
            lead.last_message = first_message
            lead.last_message_time = datetime.utcnow()
            lead.updated_at = datetime.utcnow()
            
            if sender_name and not lead.sender_name:
                lead.sender_name = sender_name
            
            db.commit()
            db.refresh(lead)
            logger.info(f"Updated lead: {phone_number} (message count: {lead.message_count})")
            return lead
        
        # Create new lead
        lead = Lead(
            phone_number=phone_number,
            sender_name=sender_name or phone_number,
            first_message=first_message,
            last_message=first_message,
            message_count=1,
            is_active=True,
            converted_to_student=False,
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Created new lead: {phone_number} - {sender_name}")
        return lead

    @staticmethod
    def get_lead_by_phone(db: Session, phone_number: str) -> Optional[Lead]:
        """Get lead by phone number."""
        return db.query(Lead).filter(Lead.phone_number == phone_number).first()

    @staticmethod
    def get_all_active_leads(db: Session, limit: int = 50) -> list:
        """Get all active leads, ordered by most recent."""
        return (
            db.query(Lead)
            .filter(Lead.is_active == True, Lead.converted_to_student == False)
            .order_by(Lead.last_message_time.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def convert_lead_to_student(db: Session, phone_number: str, student_id: int) -> Lead:
        """
        Mark a lead as converted to student.
        
        Args:
            db: Database session
            phone_number: Lead phone number
            student_id: The new Student ID
        
        Returns:
            Updated Lead object
        """
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        
        if not lead:
            raise ValueError(f"Lead with phone number {phone_number} not found")
        
        lead.converted_to_student = True
        lead.student_id = student_id
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Converted lead {phone_number} to student {student_id}")
        return lead

    @staticmethod
    def deactivate_lead(db: Session, phone_number: str) -> Lead:
        """Deactivate a lead."""
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        
        if not lead:
            raise ValueError(f"Lead with phone number {phone_number} not found")
        
        lead.is_active = False
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Deactivated lead: {phone_number}")
        return lead

    @staticmethod
    def delete_lead(db: Session, phone_number: str) -> bool:
        """Delete a lead."""
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        
        if not lead:
            return False
        
        db.delete(lead)
        db.commit()
        
        logger.info(f"Deleted lead: {phone_number}")
        return True
