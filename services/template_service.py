"""
Template Service - Manages bot response templates from settings.

Provides a centralized way to get customizable bot message templates
with support for variable substitution.
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models.settings import AdminSetting

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing and rendering bot response templates."""

    # Default templates
    DEFAULTS = {
        "template_welcome": "👋 {name}, welcome to {bot_name}!",
        "template_status": "📋 Status: Awaiting registration\n\nPlease provide:\n1. Your full name\n2. Your class/grade\n3. Email address",
        "template_greeting": "Hi {name}! What would you like to do?",
        "template_help": "📚 Help & Features\n\n🎓 I can help you with:\n📝 Homework - Submit assignments and get feedback\n💳 Subscribe - Unlimited submissions\n❓ FAQs - Quick answers\n💬 Support - Chat with our team",
        "template_faq": "❓ Frequently Asked Questions\n\nChoose a category for more info.",
        "template_error": "❓ I didn't quite understand that.\n\nChoose an option above to continue.",
    }

    @staticmethod
    def get_template(db: Session, key: str, defaults: Optional[Dict[str, str]] = None) -> str:
        """
        Get a template from settings with fallback to defaults.

        Args:
            db: Database session
            key: Template key (e.g., 'template_welcome')
            defaults: Optional custom defaults dict

        Returns:
            Template string
        """
        try:
            setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
            if setting and setting.value:
                return setting.value
        except Exception as e:
            logger.warning(f"Error fetching template '{key}' from database: {str(e)}")

        # Return default
        if defaults and key in defaults:
            return defaults[key]
        return TemplateService.DEFAULTS.get(key, "")

    @staticmethod
    def get_all_templates(db: Session) -> Dict[str, str]:
        """
        Get all templates with defaults for missing ones.

        Args:
            db: Database session

        Returns:
            Dict of all templates
        """
        templates = {}
        for key in TemplateService.DEFAULTS.keys():
            templates[key] = TemplateService.get_template(db, key)
        return templates

    @staticmethod
    def render(template: str, bot_name: str = "EduBot", name: Optional[str] = None) -> str:
        """
        Render a template with variable substitution.

        Args:
            template: Template string with {name}, {bot_name} placeholders
            bot_name: Bot name for {bot_name} placeholder
            name: User name for {name} placeholder

        Returns:
            Rendered template string
        """
        result = template.replace("{bot_name}", bot_name)
        if name:
            result = result.replace("{name}", name)
        else:
            # Remove {name} if no name provided
            result = result.replace("{name}, ", "").replace("{name}", "")
        return result

    @staticmethod
    def get_welcome_message(db: Session, name: str, bot_name: str = "EduBot") -> str:
        """Get rendered welcome message."""
        template = TemplateService.get_template(db, "template_welcome")
        return TemplateService.render(template, bot_name, name)

    @staticmethod
    def get_status_message(db: Session, bot_name: str = "EduBot") -> str:
        """Get rendered status message."""
        template = TemplateService.get_template(db, "template_status")
        return TemplateService.render(template, bot_name)

    @staticmethod
    def get_greeting_message(db: Session, name: Optional[str] = None, bot_name: str = "EduBot") -> str:
        """Get rendered greeting message."""
        template = TemplateService.get_template(db, "template_greeting")
        return TemplateService.render(template, bot_name, name)

    @staticmethod
    def get_help_message(db: Session, bot_name: str = "EduBot") -> str:
        """Get rendered help message."""
        template = TemplateService.get_template(db, "template_help")
        return TemplateService.render(template, bot_name)

    @staticmethod
    def get_faq_message(db: Session, bot_name: str = "EduBot") -> str:
        """Get rendered FAQ message."""
        template = TemplateService.get_template(db, "template_faq")
        return TemplateService.render(template, bot_name)

    @staticmethod
    def get_error_message(db: Session, bot_name: str = "EduBot") -> str:
        """Get rendered error message."""
        template = TemplateService.get_template(db, "template_error")
        return TemplateService.render(template, bot_name)
