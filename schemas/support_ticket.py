"""
Support ticket schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SupportMessageSchema(BaseModel):
    """Support message data."""
    id: int
    ticket_id: int
    sender_type: str  # 'user' or 'admin'
    sender_name: Optional[str] = None
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class SupportTicketBase(BaseModel):
    """Base support ticket data."""
    phone_number: str
    sender_name: Optional[str] = None
    issue_description: Optional[str] = None


class SupportTicketCreate(SupportTicketBase):
    """Create support ticket request."""
    student_id: Optional[int] = None


class SupportTicketUpdate(BaseModel):
    """Update support ticket request."""
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_admin_id: Optional[int] = None


class SupportTicketResponse(SupportTicketBase):
    """Support ticket response."""
    id: int
    student_id: Optional[int] = None
    status: str
    priority: str
    assigned_admin_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    messages: List[SupportMessageSchema] = []

    class Config:
        from_attributes = True


class SupportMessageCreate(BaseModel):
    """Create support message request."""
    message: str = Field(..., min_length=1, max_length=2000)


class SupportTicketListResponse(BaseModel):
    """List of support tickets response."""
    status: str
    total: int
    skip: int
    limit: int
    count: int
    data: List[SupportTicketResponse]


class SupportNotificationResponse(BaseModel):
    """Support notification data."""
    open_tickets: int
    in_progress_tickets: int
    unassigned_tickets: int
    has_alerts: bool
