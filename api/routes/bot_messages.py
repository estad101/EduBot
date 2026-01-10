"""
Bot Message Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from config.database import get_db
from models.bot_message import BotMessage, BotMessageWorkflow
from services.bot_message_service import BotMessageService, BotMessageWorkflowService
from schemas.response import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/list", response_model=StandardResponse)
async def get_messages(
    active_only: bool = Query(True),
    context: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all bot messages with optional filtering."""
    try:
        if context:
            messages = BotMessageService.get_message_by_context(db, context)
        else:
            messages = BotMessageService.get_all_messages(db, active_only=active_only)

        message_data = []
        for msg in messages:
            message_data.append({
                "id": msg.id,
                "message_key": msg.message_key,
                "message_type": msg.message_type,
                "context": msg.context,
                "content": msg.content,
                "has_menu": msg.has_menu,
                "menu_items": msg.menu_items or [],
                "next_states": msg.next_states or [],
                "is_active": msg.is_active,
                "description": msg.description,
                "variables": msg.variables or []
            })

        return StandardResponse(
            status="success",
            message=f"Found {len(message_data)} messages",
            data={"messages": message_data}
        )
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_key}", response_model=StandardResponse)
async def get_message(message_key: str, db: Session = Depends(get_db)):
    """Get a specific message by key."""
    try:
        message = BotMessageService.get_message_by_key(db, message_key)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return StandardResponse(
            status="success",
            data={
                "id": message.id,
                "message_key": message.message_key,
                "message_type": message.message_type,
                "context": message.context,
                "content": message.content,
                "has_menu": message.has_menu,
                "menu_items": message.menu_items or [],
                "next_states": message.next_states or [],
                "is_active": message.is_active,
                "description": message.description,
                "variables": message.variables or []
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=StandardResponse)
async def create_message(
    message_key: str,
    message_type: str,
    context: str,
    content: str,
    description: str = None,
    has_menu: bool = False,
    menu_items: List[dict] = None,
    next_states: List[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new bot message."""
    try:
        existing = BotMessageService.get_message_by_key(db, message_key)
        if existing:
            raise HTTPException(status_code=400, detail="Message key already exists")

        message = BotMessageService.create_message(
            db=db,
            message_key=message_key,
            message_type=message_type,
            context=context,
            content=content,
            description=description,
            has_menu=has_menu,
            menu_items=menu_items,
            next_states=next_states
        )

        return StandardResponse(
            status="success",
            message="Message created successfully",
            data={
                "id": message.id,
                "message_key": message.message_key
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{message_key}/update", response_model=StandardResponse)
async def update_message(
    message_key: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    has_menu: Optional[bool] = None,
    menu_items: Optional[List[dict]] = None,
    next_states: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update a bot message."""
    try:
        message = BotMessageService.update_message(
            db=db,
            message_key=message_key,
            content=content,
            description=description,
            has_menu=has_menu,
            menu_items=menu_items,
            next_states=next_states,
            is_active=is_active
        )

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return StandardResponse(
            status="success",
            message="Message updated successfully",
            data={"message_key": message.message_key}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{message_key}", response_model=StandardResponse)
async def delete_message(message_key: str, db: Session = Depends(get_db)):
    """Soft-delete a message by marking as inactive."""
    try:
        message = BotMessageService.update_message(
            db=db,
            message_key=message_key,
            is_active=False
        )

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return StandardResponse(
            status="success",
            message="Message deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/diagram", response_model=StandardResponse)
async def get_workflow_diagram(db: Session = Depends(get_db)):
    """Get the complete message workflow diagram."""
    try:
        diagram = BotMessageWorkflowService.get_workflow_diagram(db)
        return StandardResponse(
            status="success",
            data=diagram
        )
    except Exception as e:
        logger.error(f"Error fetching workflow diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/next/{message_key}", response_model=StandardResponse)
async def get_next_messages(
    message_key: str,
    db: Session = Depends(get_db)
):
    """Get all possible next messages from a given message."""
    try:
        workflows = BotMessageWorkflowService.get_next_messages(db, message_key)
        
        workflow_data = []
        for wf in workflows:
            workflow_data.append({
                "to_message": wf.to_message,
                "trigger": wf.trigger,
                "condition": wf.condition,
                "description": wf.description
            })

        return StandardResponse(
            status="success",
            data={"next_messages": workflow_data}
        )
    except Exception as e:
        logger.error(f"Error fetching next messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
