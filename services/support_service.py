"""
Support Ticket Service - Handle chat support requests and ticket management.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from models.support_ticket import SupportTicket, SupportMessage, TicketStatus, TicketPriority
from models.student import Student
from utils.logger import get_logger

logger = get_logger("support_service")


class SupportService:
    """Service for managing support tickets and messages."""

    @staticmethod
    def create_ticket(
        db: Session,
        phone_number: str,
        sender_name: Optional[str] = None,
        issue_description: Optional[str] = None,
        student_id: Optional[int] = None,
    ) -> SupportTicket:
        """
        Create a new support ticket.

        Args:
            db: Database session
            phone_number: User's phone number
            sender_name: Name of person requesting support
            issue_description: Description of the issue
            student_id: Student ID if registered user

        Returns:
            Created SupportTicket
        """
        # Check if user already has an open ticket
        existing = db.query(SupportTicket).filter(
            SupportTicket.phone_number == phone_number,
            SupportTicket.status == TicketStatus.OPEN,
        ).first()

        if existing:
            logger.info(f"User {phone_number} already has an open ticket #{existing.id}")
            return existing

        # Create new ticket
        ticket = SupportTicket(
            phone_number=phone_number,
            sender_name=sender_name,
            issue_description=issue_description or "Chat support requested",
            student_id=student_id,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        logger.info(f"✓ Created support ticket #{ticket.id} for {phone_number}")
        return ticket

    @staticmethod
    def add_message(
        db: Session,
        ticket_id: int,
        sender_type: str,  # 'user' or 'admin'
        message: str,
        sender_name: Optional[str] = None,
    ) -> SupportMessage:
        """
        Add a message to a support ticket.

        Args:
            db: Database session
            ticket_id: Support ticket ID
            sender_type: 'user' or 'admin'
            message: Message content
            sender_name: Name of sender

        Returns:
            Created SupportMessage
        """
        # Verify ticket exists
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket #{ticket_id} not found")

        # Create message
        support_msg = SupportMessage(
            ticket_id=ticket_id,
            sender_type=sender_type,
            message=message,
            sender_name=sender_name,
        )

        db.add(support_msg)
        db.commit()
        db.refresh(support_msg)

        logger.info(f"✓ Added message to ticket #{ticket_id}")

        # Mark ticket as IN_PROGRESS if admin responds
        if sender_type == "admin" and ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS
            ticket.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"✓ Ticket #{ticket_id} status changed to IN_PROGRESS")

        return support_msg

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[SupportTicket]:
        """
        Get a support ticket by ID.

        Args:
            db: Database session
            ticket_id: Ticket ID

        Returns:
            SupportTicket or None
        """
        return db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    @staticmethod
    def get_ticket_by_phone(db: Session, phone_number: str) -> Optional[SupportTicket]:
        """
        Get the most recent support ticket for a phone number.

        Args:
            db: Database session
            phone_number: User's phone number

        Returns:
            SupportTicket or None
        """
        return db.query(SupportTicket).filter(
            SupportTicket.phone_number == phone_number
        ).order_by(SupportTicket.created_at.desc()).first()

    @staticmethod
    def get_open_tickets(db: Session, skip: int = 0, limit: int = 50) -> List[SupportTicket]:
        """
        Get all open support tickets.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of open SupportTickets
        """
        return db.query(SupportTicket).filter(
            SupportTicket.status == TicketStatus.OPEN
        ).order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_tickets(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> tuple[List[SupportTicket], int]:
        """
        Get all support tickets with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            status: Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)

        Returns:
            Tuple of (tickets list, total count)
        """
        query = db.query(SupportTicket)

        if status:
            query = query.filter(SupportTicket.status == status)

        total = query.count()
        tickets = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit).all()

        return tickets, total

    @staticmethod
    def get_ticket_messages(db: Session, ticket_id: int) -> List[SupportMessage]:
        """
        Get all messages for a support ticket.

        Args:
            db: Database session
            ticket_id: Ticket ID

        Returns:
            List of SupportMessages
        """
        return db.query(SupportMessage).filter(
            SupportMessage.ticket_id == ticket_id
        ).order_by(SupportMessage.created_at.asc()).all()

    @staticmethod
    def update_ticket_status(
        db: Session,
        ticket_id: int,
        new_status: str,
    ) -> SupportTicket:
        """
        Update ticket status.

        Args:
            db: Database session
            ticket_id: Ticket ID
            new_status: New status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)

        Returns:
            Updated SupportTicket
        """
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket #{ticket_id} not found")

        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()

        if new_status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(ticket)

        logger.info(f"✓ Ticket #{ticket_id} status changed from {old_status} to {new_status}")
        return ticket

    @staticmethod
    def assign_ticket(db: Session, ticket_id: int, admin_id: int) -> SupportTicket:
        """
        Assign a ticket to an admin.

        Args:
            db: Database session
            ticket_id: Ticket ID
            admin_id: Admin user ID

        Returns:
            Updated SupportTicket
        """
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket #{ticket_id} not found")

        ticket.assigned_admin_id = admin_id
        ticket.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)

        logger.info(f"✓ Ticket #{ticket_id} assigned to admin #{admin_id}")
        return ticket

    @staticmethod
    def get_admin_tickets(
        db: Session,
        admin_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[SupportTicket]:
        """
        Get all tickets assigned to an admin.

        Args:
            db: Database session
            admin_id: Admin user ID
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of SupportTickets
        """
        return db.query(SupportTicket).filter(
            SupportTicket.assigned_admin_id == admin_id
        ).order_by(SupportTicket.updated_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_unassigned_tickets(db: Session) -> List[SupportTicket]:
        """
        Get all unassigned open tickets.

        Args:
            db: Database session

        Returns:
            List of unassigned SupportTickets
        """
        return db.query(SupportTicket).filter(
            SupportTicket.assigned_admin_id == None,
            SupportTicket.status == TicketStatus.OPEN,
        ).order_by(SupportTicket.created_at.asc()).all()

    @staticmethod
    def get_notifications(db: Session) -> Dict[str, Any]:
        """
        Get support notifications for dashboard (open tickets count).

        Args:
            db: Database session

        Returns:
            Notification dict
        """
        open_count = db.query(SupportTicket).filter(
            SupportTicket.status == TicketStatus.OPEN
        ).count()

        in_progress = db.query(SupportTicket).filter(
            SupportTicket.status == TicketStatus.IN_PROGRESS
        ).count()

        unassigned = db.query(SupportTicket).filter(
            SupportTicket.assigned_admin_id == None,
            SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
        ).count()

        return {
            "open_tickets": open_count,
            "in_progress_tickets": in_progress,
            "unassigned_tickets": unassigned,
            "has_alerts": open_count > 0 or unassigned > 0,
        }
