"""
Support ticket API routes.

Handles chat support requests, ticket management, and admin responses.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from config.database import get_db
from models.support_ticket import SupportTicket
from services.support_service import SupportService
from services.student_service import StudentService
from services.whatsapp_service import WhatsAppService
from schemas.support_ticket import (
    SupportTicketCreate,
    SupportTicketResponse,
    SupportTicketListResponse,
    SupportMessageCreate,
    SupportNotificationResponse,
)
from schemas.response import StandardResponse
from utils.logger import get_logger

logger = get_logger("support_routes")

router = APIRouter(prefix="/api/support", tags=["support"])


@router.post("/tickets", response_model=StandardResponse)
async def create_support_ticket(
    request: SupportTicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket from WhatsApp bot.

    This is called when a user selects "Chat Support" from the menu.
    """
    try:
        logger.info(f"📞 Creating support ticket for {request.phone_number}")

        # Create ticket
        ticket = SupportService.create_ticket(
            db,
            phone_number=request.phone_number,
            sender_name=request.sender_name,
            issue_description=request.issue_description,
            student_id=request.student_id,
        )

        logger.info(f"✓ Support ticket #{ticket.id} created")

        return StandardResponse(
            status="success",
            message="Support ticket created",
            data={
                "ticket_id": ticket.id,
                "status": ticket.status,
                "phone_number": ticket.phone_number,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error creating support ticket: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="SUPPORT_TICKET_ERROR",
        )


@router.post("/tickets/{ticket_id}/messages", response_model=StandardResponse)
async def add_message_to_ticket(
    ticket_id: int,
    request: SupportMessageCreate,
    sender_type: str = Query("user", pattern="^(user|admin)$"),
    db: Session = Depends(get_db)
):
    """
    Add a message to a support ticket.

    Args:
        ticket_id: Support ticket ID
        request: Message content
        sender_type: 'user' or 'admin'
    """
    try:
        logger.info(f"💬 Adding {sender_type} message to ticket #{ticket_id}")

        # Verify ticket exists
        ticket = SupportService.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Add message
        message = SupportService.add_message(
            db,
            ticket_id=ticket_id,
            sender_type=sender_type,
            message=request.message,
            sender_name=f"Support Admin" if sender_type == "admin" else ticket.sender_name,
        )

        logger.info(f"✓ Message added to ticket #{ticket_id}")

        # If admin message, send WhatsApp notification to user
        if sender_type == "admin":
            try:
                # Send message with End Chat button
                await WhatsAppService.send_interactive_message(
                    phone_number=ticket.phone_number,
                    body_text=request.message,
                    buttons=[
                        {"id": "end_chat", "title": "🛑 End Chat"},
                    ]
                )
                logger.info(f"✓ WhatsApp notification sent to {ticket.phone_number}")
            except Exception as e:
                logger.warning(f"⚠️ Could not send WhatsApp notification: {str(e)}")

        return StandardResponse(
            status="success",
            message="Message added",
            data={"message_id": message.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding message: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="MESSAGE_ERROR",
        )


@router.get("/tickets/{ticket_id}", response_model=StandardResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a support ticket with all messages.

    Args:
        ticket_id: Support ticket ID
    """
    try:
        ticket = SupportService.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Get messages
        messages = SupportService.get_ticket_messages(db, ticket_id)

        ticket_data = {
            "id": ticket.id,
            "phone_number": ticket.phone_number,
            "sender_name": ticket.sender_name,
            "issue_description": ticket.issue_description,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_admin_id": ticket.assigned_admin_id,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "resolved_at": ticket.resolved_at,
            "messages": [
                {
                    "id": m.id,
                    "ticket_id": m.ticket_id,
                    "sender_type": m.sender_type,
                    "sender_name": m.sender_name,
                    "message": m.message,
                    "created_at": m.created_at,
                }
                for m in messages
            ]
        }

        return StandardResponse(
            status="success",
            message="Ticket retrieved",
            data=ticket_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving ticket: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="RETRIEVAL_ERROR",
        )


@router.get("/open-tickets", response_model=StandardResponse)
async def get_open_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all open support tickets.

    This is used by the dashboard to show alerts.
    """
    try:
        tickets = SupportService.get_open_tickets(db, skip=skip, limit=limit)

        return StandardResponse(
            status="success",
            message="Open tickets retrieved",
            count=len(tickets),
            data=[
                {
                    "id": t.id,
                    "phone_number": t.phone_number,
                    "sender_name": t.sender_name,
                    "status": t.status,
                    "priority": t.priority,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at,
                    "message_count": len(t.messages),
                }
                for t in tickets
            ]
        )

    except Exception as e:
        logger.error(f"❌ Error retrieving open tickets: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="RETRIEVAL_ERROR",
        )


@router.get("/notifications", response_model=StandardResponse)
async def get_support_notifications(
    db: Session = Depends(get_db)
):
    """
    Get support notifications for dashboard alerts.

    Returns count of open and unassigned tickets.
    """
    try:
        notifications = SupportService.get_notifications(db)

        return StandardResponse(
            status="success",
            message="Notifications retrieved",
            data=notifications
        )

    except Exception as e:
        logger.error(f"❌ Error getting notifications: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="NOTIFICATION_ERROR",
        )
