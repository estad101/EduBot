"""
Bot Message Model - stores configurable bot response messages and menus.
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON
from datetime import datetime
from config.database import Base


class BotMessage(Base):
    """
    Bot Message model - stores all bot response messages.
    
    Fields:
        id: Primary key
        message_key: Unique identifier for the message (e.g., 'registration_name_prompt')
        message_type: Type of message (greeting, prompt, confirmation, menu, error, info)
        context: Conversation state/context where this message appears
        content: The actual message text to send to user
        has_menu: Whether this message has menu buttons
        menu_items: JSON array of menu items [{label, action, description}]
        next_states: JSON array of possible next conversation states
        is_active: Whether this message is currently active/used
        description: Admin description of what this message is for
        variables: JSON array of variables that can be used in content {full_name}, {bot_name}, etc
        created_at: Creation timestamp
        updated_at: Last update timestamp
        created_by: Admin user who created this
        updated_by: Admin user who last updated this
    """
    __tablename__ = "bot_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_key = Column(String(255), unique=True, nullable=False, index=True)
    message_type = Column(String(50), nullable=False, index=True)  # greeting, prompt, confirmation, menu, error, info
    context = Column(String(100), nullable=False, index=True)  # The conversation state
    content = Column(Text, nullable=False)
    has_menu = Column(Boolean, default=False)
    menu_items = Column(JSON, default=None)  # [{id, label, action, emoji, description}]
    next_states = Column(JSON, default=None)  # [next_state1, next_state2]
    is_active = Column(Boolean, default=True, index=True)
    description = Column(Text, nullable=True)
    variables = Column(JSON, default=None)  # {full_name, bot_name, email, etc}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<BotMessage(key='{self.message_key}', type='{self.message_type}')>"


class BotMessageTemplate(Base):
    """
    Message Templates - reusable templates for common message patterns.
    
    Fields:
        id: Primary key
        template_name: Unique template name
        template_content: Template content with variables
        variables: Available variables for this template
        is_default: Whether this is a default/built-in template
    """
    __tablename__ = "bot_message_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), unique=True, nullable=False, index=True)
    template_content = Column(Text, nullable=False)
    variables = Column(JSON, default=None)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<BotMessageTemplate(name='{self.template_name}')>"


class BotMessageWorkflow(Base):
    """
    Message Workflow - defines how messages connect together.
    
    Fields:
        id: Primary key
        workflow_name: Unique workflow name
        from_message: Source message key
        to_message: Target message key
        trigger: What causes the transition (user_action, timeout, condition)
        condition: Optional condition for the transition
        description: Workflow step description
    """
    __tablename__ = "bot_message_workflows"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(255), nullable=False, index=True)
    from_message = Column(String(255), nullable=False)
    to_message = Column(String(255), nullable=False)
    trigger = Column(String(50), nullable=False)  # user_action, timeout, condition, menu_selection
    condition = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<BotMessageWorkflow({self.from_message} -> {self.to_message})>"
