"""
Bot Message Service - manages bot messages and templates.
Integrates bot name from admin_settings for personalized messages.
"""
import logging
import time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models.bot_message import BotMessage, BotMessageTemplate, BotMessageWorkflow

logger = logging.getLogger(__name__)

# Bot name cache for message personalization
_bot_name_cache = {'value': 'EduBot', 'timestamp': None}
_CACHE_TTL = 3600  # 1 hour


class BotMessageService:
    """Service for managing bot messages."""

    @staticmethod
    def get_bot_name(db: Session = None) -> str:
        """
        Get the bot name from database with caching.
        Used for personalizing bot messages.
        """
        now = time.time()
        
        # Return cached value if still valid
        if _bot_name_cache['timestamp'] and (now - _bot_name_cache['timestamp']) < _CACHE_TTL:
            return _bot_name_cache['value']
        
        # Try to fetch from database
        if db:
            try:
                from models.settings import AdminSetting
                setting = db.query(AdminSetting).filter(
                    AdminSetting.key == 'bot_name'
                ).first()
                if setting and setting.value:
                    _bot_name_cache['value'] = setting.value
                    _bot_name_cache['timestamp'] = now
                    logger.info(f"Bot name updated to: {setting.value}")
                    return setting.value
            except Exception as e:
                logger.warning(f"Failed to fetch bot name from DB: {e}")
        
        return _bot_name_cache['value']

    @staticmethod
    def personalize_message(content: str, db: Session = None, variables: Dict[str, str] = None) -> str:
        """
        Personalize message content with bot name and other variables.
        Replaces {bot_name} placeholder with actual bot name from database.
        """
        bot_name = BotMessageService.get_bot_name(db)
        
        # Replace bot name placeholder
        content = content.replace('{bot_name}', bot_name)
        
        # Replace other variables if provided
        if variables:
            for key, value in variables.items():
                placeholder = '{' + key + '}'
                content = content.replace(placeholder, str(value))
        
        return content

    @staticmethod
    def get_message_by_key(db: Session, message_key: str) -> Optional[BotMessage]:
        """Get a message by its key."""
        return db.query(BotMessage).filter(
            BotMessage.message_key == message_key,
            BotMessage.is_active == True
        ).first()

    @staticmethod
    def get_message_by_context(db: Session, context: str) -> List[BotMessage]:
        """Get all messages for a given context/state."""
        return db.query(BotMessage).filter(
            BotMessage.context == context,
            BotMessage.is_active == True
        ).all()

    @staticmethod
    def create_message(
        db: Session,
        message_key: str,
        message_type: str,
        context: str,
        content: str,
        description: str = None,
        has_menu: bool = False,
        menu_items: List[Dict] = None,
        next_states: List[str] = None,
        variables: List[str] = None,
        created_by: str = "system"
    ) -> BotMessage:
        """Create a new bot message."""
        message = BotMessage(
            message_key=message_key,
            message_type=message_type,
            context=context,
            content=content,
            description=description,
            has_menu=has_menu,
            menu_items=menu_items or [],
            next_states=next_states or [],
            variables=variables or [],
            created_by=created_by
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.info(f"Created message: {message_key}")
        return message

    @staticmethod
    def update_message(
        db: Session,
        message_key: str,
        content: str = None,
        description: str = None,
        has_menu: bool = None,
        menu_items: List[Dict] = None,
        next_states: List[str] = None,
        is_active: bool = None,
        updated_by: str = "system"
    ) -> Optional[BotMessage]:
        """Update an existing message."""
        message = db.query(BotMessage).filter(
            BotMessage.message_key == message_key
        ).first()
        
        if not message:
            logger.warning(f"Message not found: {message_key}")
            return None

        if content is not None:
            message.content = content
        if description is not None:
            message.description = description
        if has_menu is not None:
            message.has_menu = has_menu
        if menu_items is not None:
            message.menu_items = menu_items
        if next_states is not None:
            message.next_states = next_states
        if is_active is not None:
            message.is_active = is_active
        
        message.updated_by = updated_by

        db.commit()
        db.refresh(message)
        logger.info(f"Updated message: {message_key}")
        return message

    @staticmethod
    def get_all_messages(db: Session, active_only: bool = True) -> List[BotMessage]:
        """Get all messages."""
        query = db.query(BotMessage)
        if active_only:
            query = query.filter(BotMessage.is_active == True)
        return query.order_by(BotMessage.context, BotMessage.message_type).all()

    @staticmethod
    def render_message(message: BotMessage, variables: Dict[str, str] = None) -> str:
        """
        Render a message by replacing variables with values.
        
        Example: "Hello {full_name}!" with {full_name: "John"} -> "Hello John!"
        """
        content = message.content
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
        return content


class BotMessageWorkflowService:
    """Service for managing message workflows."""

    @staticmethod
    def get_next_messages(db: Session, from_message: str) -> List[BotMessageWorkflow]:
        """Get all possible next messages from a given message."""
        return db.query(BotMessageWorkflow).filter(
            BotMessageWorkflow.from_message == from_message
        ).all()

    @staticmethod
    def create_workflow(
        db: Session,
        workflow_name: str,
        from_message: str,
        to_message: str,
        trigger: str,
        condition: str = None,
        description: str = None
    ) -> BotMessageWorkflow:
        """Create a workflow connection."""
        workflow = BotMessageWorkflow(
            workflow_name=workflow_name,
            from_message=from_message,
            to_message=to_message,
            trigger=trigger,
            condition=condition,
            description=description
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        logger.info(f"Created workflow: {workflow_name}")
        return workflow

    @staticmethod
    def get_workflow_diagram(db: Session) -> Dict[str, Any]:
        """Get complete workflow diagram."""
        workflows = db.query(BotMessageWorkflow).all()
        messages = db.query(BotMessage).filter(BotMessage.is_active == True).all()

        # Build nodes (messages)
        nodes = []
        for msg in messages:
            nodes.append({
                "id": msg.message_key,
                "label": msg.message_key,
                "type": msg.message_type,
                "context": msg.context
            })

        # Build edges (workflows)
        edges = []
        for wf in workflows:
            edges.append({
                "from": wf.from_message,
                "to": wf.to_message,
                "trigger": wf.trigger,
                "condition": wf.condition,
                "description": wf.description
            })

        return {
            "nodes": nodes,
            "edges": edges
        }
