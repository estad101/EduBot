"""
Conversation State Management Service.

Tracks user conversation state across multiple message exchanges.
Manages registration, homework submission, and payment flows.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import time

logger = logging.getLogger(__name__)

# Global bot name cache (will be populated from database)
_bot_name_cache = {'value': 'EduBot', 'timestamp': None}
_BOT_NAME_CACHE_TTL = 3600  # 1 hour

# Import NotificationTrigger for chat notifications
try:
    from services.notification_trigger import NotificationTrigger
except ImportError:
    NotificationTrigger = None

# Conversation states
class ConversationState(str, Enum):
    """User conversation states."""

    INITIAL = "initial"  # New user
    IDENTIFYING = "identifying"  # Checking if existing user
    REGISTERING_NAME = "registering_name"
    REGISTERING_EMAIL = "registering_email"
    REGISTERING_CLASS = "registering_class"
    UPDATING_NAME = "updating_name"
    UPDATING_EMAIL = "updating_email"
    UPDATING_CLASS = "updating_class"
    ALREADY_REGISTERED = "already_registered"  # User tried to register but already has account
    REGISTERED = "registered"
    HOMEWORK_SUBJECT = "homework_subject"
    HOMEWORK_TYPE = "homework_type"
    HOMEWORK_CONTENT = "homework_content"
    HOMEWORK_SUBMITTED = "homework_submitted"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CONFIRMED = "payment_confirmed"
    CHAT_SUPPORT_ACTIVE = "chat_support_active"  # User is in active chat with admin
    IDLE = "idle"  # Idle state waiting for input


# In-memory storage for conversation state
# In production, this should be stored in database
_conversation_states: Dict[str, Dict[str, Any]] = {}


class ConversationService:
    """Service for managing user conversation state."""

    TIMEOUT_MINUTES = 30  # Conversation timeout

    @staticmethod
    def get_bot_name(db=None) -> str:
        """
        Get the bot name from database cache or default.
        Caches for 1 hour to avoid repeated DB queries.
        """
        now = time.time()
        
        # Return cached value if still valid
        if _bot_name_cache['timestamp'] and (now - _bot_name_cache['timestamp']) < _BOT_NAME_CACHE_TTL:
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
        
        # Return cached value or default
        return _bot_name_cache['value']
    
    @staticmethod
    def set_bot_name_cache(bot_name: str):
        """Update the cached bot name."""
        _bot_name_cache['value'] = bot_name
        _bot_name_cache['timestamp'] = time.time()
        logger.info(f"Bot name cache updated to: {bot_name}")

    @staticmethod
    def get_available_features_menu(db=None, first_name: str = "") -> str:
        """
        Get the available features menu message from database template.
        Falls back to hardcoded version if template not found.
        Substitutes variables like {full_name} and {bot_name}.
        """
        # Try to fetch from database
        if db:
            try:
                from models.bot_message import BotMessageTemplate
                template = db.query(BotMessageTemplate).filter(
                    BotMessageTemplate.template_name == "available_features"
                ).first()
                if template and template.template_content:
                    content = template.template_content
                    # Replace variables in template
                    content = content.replace("{full_name}", first_name if first_name else "there")
                    content = content.replace("{bot_name}", ConversationService.get_bot_name(db))
                    return content
            except Exception as e:
                logger.warning(f"Failed to fetch template from DB: {e}")
        
        # Fallback to hardcoded version
        greeting = f"Hey {first_name}!" if first_name else "Hey there!"
        feature_text = (
            f"{greeting}\n\n"
            f"AVAILABLE FEATURES:\n\n"
            f"[Home] **Home** - Return to home menu\n"
            f"[?] **FAQ** - Get answers to common questions\n"
            f"[Book] **Homework** - Submit your homework\n"
            f"[Chat] **Support** - Chat with our team\n"
            f"[Card] **Subscribe** - View subscription plans\n"
            f"[Info] **Status** - Check your account details\n"
            f"[Help] **Help** - Get help with the bot\n\n"
            f"Just type a command above to get started!"
        )
        return feature_text

    @staticmethod
    def get_faq_menu(db=None) -> str:
        """
        Get the FAQ menu message from database template.
        Falls back to hardcoded version if template not found.
        """
        # Try to fetch from database
        if db:
            try:
                from models.bot_message import BotMessageTemplate
                template = db.query(BotMessageTemplate).filter(
                    BotMessageTemplate.template_name == "faq_main"
                ).first()
                if template and template.template_content:
                    return template.template_content
            except Exception as e:
                logger.warning(f"Failed to fetch FAQ template from DB: {e}")
        
        # Fallback to hardcoded version
        faq_text = (
            "[?] Frequently Asked Questions\n\n"
            "[Pen] Registration: Create account with name, email, class - it's FREE!\n\n"
            "[Book] Homework: Submit text or images. Get tutor responses within 24 hours.\n\n"
            "[Card] Payment: Subscribers enjoy unlimited homework submissions.\n\n"
            "[Star] Subscription: Get premium access for continuous learning support."
        )
        return faq_text

    @staticmethod
    def get_template(template_name: str, db=None, variables: Dict[str, str] = None) -> str:
        """
        Generic template fetcher - gets any template by name.
        Substitutes variables if provided.
        
        Args:
            template_name: Name of the template to fetch
            db: Database session
            variables: Dict of variables to substitute (e.g., {full_name: "Victor"})
        
        Returns:
            Template content with variables substituted
        """
        if db:
            try:
                from models.bot_message import BotMessageTemplate
                template = db.query(BotMessageTemplate).filter(
                    BotMessageTemplate.template_name == template_name
                ).first()
                if template and template.template_content:
                    content = template.template_content
                    # Substitute variables if provided
                    if variables:
                        for key, value in variables.items():
                            content = content.replace(f"{{{key}}}", str(value))
                    return content
            except Exception as e:
                logger.warning(f"Failed to fetch template '{template_name}' from DB: {e}")
        
        # Return empty string if not found
        return ""

    @staticmethod
    def get_state(phone_number: str) -> Dict[str, Any]:
        """
        Get conversation state for a user.

        Args:
            phone_number: User's phone number

        Returns:
            Conversation state dict
        """
        if phone_number not in _conversation_states:
            _conversation_states[phone_number] = {
                "state": ConversationState.INITIAL,
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "data": {},
            }

        state = _conversation_states[phone_number]

        # Check if conversation timed out
        if datetime.now() - state["last_updated"] > timedelta(
            minutes=ConversationService.TIMEOUT_MINUTES
        ):
            logger.info(f"Conversation timeout for {phone_number}, resetting state")
            state["state"] = ConversationState.INITIAL
            state["data"] = {}

        return state

    @staticmethod
    def set_state(phone_number: str, new_state: ConversationState):
        """
        Set conversation state for a user.

        Args:
            phone_number: User's phone number
            new_state: New conversation state
        """
        state = ConversationService.get_state(phone_number)
        state["state"] = new_state
        state["last_updated"] = datetime.now()
        logger.debug(f"User {phone_number} state changed to {new_state}")

    @staticmethod
    def set_data(phone_number: str, key: str, value: Any):
        """
        Store data in conversation context.

        Args:
            phone_number: User's phone number
            key: Data key (e.g., 'full_name', 'email')
            value: Data value
        """
        state = ConversationService.get_state(phone_number)
        state["data"][key] = value
        state["last_updated"] = datetime.now()

    @staticmethod
    def get_data(phone_number: str, key: str, default: Any = None) -> Any:
        """
        Get data from conversation context.

        Args:
            phone_number: User's phone number
            key: Data key
            default: Default value if key doesn't exist

        Returns:
            Data value or default
        """
        state = ConversationService.get_state(phone_number)
        return state.get("data", {}).get(key, default)

    @staticmethod
    def clear_state(phone_number: str):
        """
        Clear conversation state for a user.

        Args:
            phone_number: User's phone number
        """
        if phone_number in _conversation_states:
            del _conversation_states[phone_number]
            logger.info(f"Cleared conversation state for {phone_number}")

    @staticmethod
    def get_registration_data(phone_number: str) -> Dict[str, Any]:
        """
        Get collected registration data.

        Args:
            phone_number: User's phone number

        Returns:
            Registration data dict
        """
        return {
            "phone_number": phone_number,
            "full_name": ConversationService.get_data(phone_number, "full_name"),
            "email": ConversationService.get_data(phone_number, "email"),
            "class_grade": ConversationService.get_data(phone_number, "class_grade"),
        }

    @staticmethod
    def get_homework_data(phone_number: str) -> Dict[str, Any]:
        """
        Get collected homework data.

        Args:
            phone_number: User's phone number

        Returns:
            Homework data dict
        """
        return {
            "subject": ConversationService.get_data(phone_number, "homework_subject"),
            "submission_type": ConversationService.get_data(
                phone_number, "homework_type"
            ),
            "content": ConversationService.get_data(phone_number, "homework_content"),
            "file_path": ConversationService.get_data(phone_number, "file_path"),
        }

    @staticmethod
    def reset_homework_state(phone_number: str):
        """
        Reset homework-related state.

        Args:
            phone_number: User's phone number
        """
        state = ConversationService.get_state(phone_number)
        for key in ["homework_subject", "homework_type", "homework_content", "file_path"]:
            if key in state.get("data", {}):
                del state["data"][key]
        ConversationService.set_state(phone_number, ConversationState.IDLE)
        logger.debug(f"Reset homework state for {phone_number}")


class MessageRouter:
    """Route messages to appropriate handlers based on conversation state."""

    # Message keywords for routing
    KEYWORD_REGISTER = ["register", "reg", "new", "start"]
    KEYWORD_HOMEWORK = ["homework", "submit", "hand in", "assignment"]
    KEYWORD_PAY = ["pay", "payment", "subscribe", "buy"]
    KEYWORD_CHECK = ["status", "check", "subscription", "active"]
    KEYWORD_HELP = ["help", "info", "how", "menu", "options"]
    KEYWORD_FAQ = ["faq", "faqs", "frequently asked", "question", "questions"]
    KEYWORD_SUPPORT = ["support", "chat", "help me", "agent", "human", "talk to someone"]
    KEYWORD_MAIN_MENU = ["main_menu", "main menu"]
    KEYWORD_END_CHAT = ["end chat", "end_chat", "close", "done", "quit chat", "exit"]
    KEYWORD_IMAGE = ["image", "📷", "photo", "picture", "img"]
    KEYWORD_TEXT = ["text", "📄", "write", "type", "message"]
    KEYWORD_CANCEL = ["cancel", "stop", "reset", "clear", "menu"]
    KEYWORD_UPDATE = ["update", "edit", "change", "modify", "profile"]

    @staticmethod
    def get_buttons(intent: str, current_state: ConversationState, is_registered: bool = False, phone_number: str = None) -> Optional[List[Dict[str, str]]]:
        """
        Get interactive buttons for a given state.
        
        Shows buttons only when there are 3 or fewer command options.
        
        Args:
            intent: Current user intent
            current_state: Current conversation state
            is_registered: Whether user is registered
            phone_number: User's phone number (for menu state lookup)

        Returns:
            List of buttons if 3 or fewer options, None for text-based lists
        """
        # Show buttons for states with limited options (3 or fewer)
        
        # Already registered - user tried to register but has account - 2 options
        if current_state == ConversationState.ALREADY_REGISTERED:
            return [
                {"id": "update", "title": "[Pen] Update"},
                {"id": "home", "title": "[Home] Home"},
            ]
        
        # Homework type selection - 2 options
        if current_state == ConversationState.HOMEWORK_TYPE:
            return [
                {"id": "text", "title": "[Text] Text"},
                {"id": "image", "title": "[Img] Image"},
            ]
        
        # Payment confirmation - 1 option  
        if current_state == ConversationState.PAYMENT_PENDING:
            return [
                {"id": "confirm", "title": "[✓] Confirm Payment"},
            ]
        
        # FAQ menu - 4 options
        if intent == "faq":
            return [
                {"id": "faq_register", "title": "[Pen] Registration"},
                {"id": "faq_homework", "title": "[Book] Homework"},
                {"id": "faq_payment", "title": "[Card] Payment"},
                {"id": "faq_subscription", "title": "[Star] Subscription"},
            ]
        
        # All other states - use text-based lists instead of buttons
        return None

    @staticmethod
    def extract_intent(message_text: str) -> str:
        """
        Extract user intent from message text.

        Args:
            message_text: User's message text

        Returns:
            Intent string (register, homework, pay, check, help, cancel, unknown)
        """
        text_lower = message_text.lower().strip()

        # Check for main_menu FIRST (highest priority) to prevent "menu" keyword from matching help
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_MAIN_MENU):
            return "main_menu"
        
        # Check for end_chat BEFORE support (to prevent "chat" from being caught by support)
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_END_CHAT):
            return "end_chat"
        
        # Check for other keywords
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_REGISTER):
            return "register"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_UPDATE):
            return "update"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_HOMEWORK):
            return "homework"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_PAY):
            return "pay"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_CHECK):
            return "check"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_IMAGE):
            return "image"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_TEXT):
            return "text"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_FAQ):
            return "faq"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_SUPPORT):
            return "support"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_HELP):
            return "help"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_CANCEL):
            return "cancel"

        return "unknown"

    @staticmethod
    def get_next_response(
        phone_number: str, message_text: str, student_data: Optional[Dict] = None, db: Any = None
    ) -> tuple[str, Optional[ConversationState]]:
        """
        Get the next response based on conversation state and message.

        Args:
            phone_number: User's phone number
            message_text: User's message text
            student_data: Optional student data from database (includes name, status, etc.)
            db: Optional database session for notification triggers

        Returns:
            Tuple of (response_message, next_state)
        """
        state = ConversationService.get_state(phone_number)
        current_state = state.get("state")
        intent = MessageRouter.extract_intent(message_text)
        
        # Extract first name for personalization
        first_name = None
        if student_data and student_data.get("name"):
            first_name = student_data.get("name").split()[0]

        # PRIORITY: If user is in active chat support, handle their message in chat context
        # (except for end_chat intent which is handled below)
        if current_state == ConversationState.CHAT_SUPPORT_ACTIVE and intent != "end_chat":
            # User sent a message during active chat - store it and notify admin
            # Mark chat session as active with timestamp
            ConversationService.set_data(phone_number, "chat_support_active", True)
            ConversationService.set_data(phone_number, "chat_last_message_time", datetime.now().isoformat())
            
            # Store the message content for admin review via conversations page
            chat_messages = ConversationService.get_data(phone_number, "chat_messages") or []
            if isinstance(chat_messages, str):
                chat_messages = []
            chat_messages.append({
                "text": message_text,
                "timestamp": datetime.now().isoformat(),
                "sender": "user"
            })
            ConversationService.set_data(phone_number, "chat_messages", chat_messages)
            
            # Trigger admin notification for user message
            if NotificationTrigger and db:
                try:
                    user_name = student_data.get("name") if student_data else "Unknown User"
                    message_preview = message_text[:100]
                    NotificationTrigger.on_chat_user_message_admin(
                        phone_number=phone_number,
                        user_name=user_name,
                        message_preview=message_preview,
                        admin_phone="admin",
                        db=db
                    )
                except Exception as e:
                    logger.warning(f"Could not send admin message notification: {str(e)}")
            
            # Acknowledge message to user
            ack_message = (
                "✓ Your message has been sent to support.\n\n"
                "An admin will respond shortly. You can continue typing or select 'End Chat' to exit."
            )
            return (ack_message, ConversationState.CHAT_SUPPORT_ACTIVE)

        # Handle end chat command
        if intent == "end_chat":
            try:
                # Close the support ticket if one is open
                ticket_id = ConversationService.get_data(phone_number, "support_ticket_id")
                if ticket_id:
                    from services.support_service import SupportService
                    from config.database import SessionLocal
                    db_temp = SessionLocal()
                    try:
                        SupportService.update_ticket_status(db_temp, ticket_id, "CLOSED")
                    finally:
                        db_temp.close()
                
                # Calculate chat duration
                duration_minutes = None
                chat_start_time = ConversationService.get_data(phone_number, "chat_start_time")
                if chat_start_time:
                    try:
                        start_dt = datetime.fromisoformat(chat_start_time)
                        duration = datetime.now() - start_dt
                        duration_minutes = int(duration.total_seconds() / 60)
                    except:
                        pass
                
                # Trigger notification that user ended chat
                if NotificationTrigger and db:
                    try:
                        user_name = student_data.get("name") if student_data else "User"
                        NotificationTrigger.on_chat_support_ended_admin(
                            phone_number=phone_number,
                            user_name=user_name,
                            admin_phone="admin",
                            duration_minutes=duration_minutes,
                            db=db
                        )
                    except Exception as e:
                        logger.warning(f"Could not send chat ended notification: {str(e)}")
                
                # Clear support data
                ConversationService.set_data(phone_number, "requesting_support", False)
                ConversationService.set_data(phone_number, "support_ticket_id", None)
                # Clear chat support flags
                ConversationService.set_data(phone_number, "in_chat_support", False)
                ConversationService.set_data(phone_number, "chat_support_active", False)
                ConversationService.set_data(phone_number, "chat_start_time", None)
            except Exception as e:
                logger.warning(f"Could not close support ticket: {str(e)}")
            
            # Return to appropriate state based on registration
            if student_data and student_data.get("name"):
                # Registered user - return to main menu
                first_name = student_data.get("name", "").split()[0] if student_data.get("name") else ""
                feature_text = ConversationService.get_available_features_menu(db, first_name)
                return (
                    feature_text,
                    ConversationState.IDLE,
                )
            else:
                # Unregistered user - return to idle menu, not back to initial registration
                try:
                    from models.admin_settings import AdminSettings
                    from config.database import SessionLocal
                    db = SessionLocal()
                    try:
                        settings = db.query(AdminSettings).first()
                        bot_name = settings.bot_name if settings and settings.bot_name else "EduBot"
                    finally:
                        db.close()
                except Exception as e:
                    logger.warning(f"Could not fetch bot name: {str(e)}")
                    bot_name = "EduBot"
                
                menu_text = (
                    f"👋 Welcome back! I'm {bot_name}, your AI tutor assistant.\n\n"
                    f"📚 **WHAT I CAN DO** 📚\n\n"
                    f"✏️ **homework** - Get help with your assignments\n"
                    f"❓ **faq** - Find answers to common questions\n"
                    f"💬 **support** - Chat with our support team\n"
                    f"💳 **subscribe** - Check subscription plans & pricing\n"
                    f"📊 **status** - View your account info\n"
                    f"ℹ️ **help** - Learn how to use me\n\n"
                    f"Type any command above to get started or enter your name to register!"
                )
                return (
                    menu_text,
                    ConversationState.IDLE,
                )

        # Handle cancel command - Clear current flow and return to menu
        if intent == "cancel":
            # Clear any in-progress homework data
            if current_state in [ConversationState.HOMEWORK_SUBJECT, ConversationState.HOMEWORK_TYPE, ConversationState.HOMEWORK_CONTENT]:
                # User cancelled homework submission - clear homework data
                ConversationService.set_data(phone_number, "homework_subject", None)
                ConversationService.set_data(phone_number, "homework_type", None)
                ConversationService.set_data(phone_number, "homework_content", None)
                
                greeting = f"Homework submission cancelled, {first_name}." if first_name else "Homework submission cancelled."
                # Use template if available, otherwise use greeting + fallback menu
                menu_text = greeting + "\n\n" + ConversationService.get_available_features_menu(db).split("\n\n", 1)[1] if db else greeting + "\n\n" + ConversationService.get_available_features_menu(None).split("\n\n", 1)[1]
                return (
                    menu_text,
                    ConversationState.IDLE,
                )
            else:
                # Generic cancel - just show menu
                menu_text = ConversationService.get_available_features_menu(db, first_name)
                return (
                    menu_text,
                    ConversationState.IDLE,
                )

        # Handle help command - Show comprehensive feature list
        if intent == "help":
            help_text = ConversationService.get_template("help_main", db)
            if not help_text:
                # Fallback if template not found
                help_text = (
                    "[?] Help & Features\n\n"
                    "[Book] HOMEWORK SUBMISSION\n"
                    "• Submit text or images easily\n"
                    "• Get detailed tutor feedback within 24 hours\n"
                    "• Track all your submissions\n\n"
                    "[Card] PAYMENT OPTIONS\n"
                    "• FREE: Per-submission payment\n"
                    "• PREMIUM: 5000/month unlimited\n"
                    "• Priority support for subscribers\n\n"
                    "[Chat] LIVE CHAT SUPPORT\n"
                    "• Talk directly with support team\n\n"
                    "Ready to get started? Type a command!"
                )
            return (help_text, ConversationState.IDLE)

        # Handle chat support command
        if intent == "support":
            variables = {"first_name": first_name} if first_name else {}
            support_text = ConversationService.get_template("support_welcome", db, variables)
            if not support_text:
                greeting = f"Hi {first_name}! 💬" if first_name else "💬"
                support_text = (
                    f"{greeting}\n\n"
                    f"📞 Live Chat Support\n\n"
                    f"You are now connected to our support team! 🎯\n\n"
                    f"Please describe your issue and an admin will respond to you shortly.\n\n"
                    f"You can continue chatting until you select 'End Chat' to return to the main menu."
                )
            # Store that user is now in active chat support
            ConversationService.set_data(phone_number, "in_chat_support", True)
            ConversationService.set_data(phone_number, "chat_support_active", True)
            ConversationService.set_data(phone_number, "chat_start_time", datetime.now().isoformat())
            
            # Trigger admin notification
            if NotificationTrigger and db:
                try:
                    user_name = student_data.get("name") if student_data else "Unknown User"
                    NotificationTrigger.on_chat_support_initiated_admin(
                        phone_number=phone_number,
                        user_name=user_name,
                        admin_phone="admin",
                        db=db
                    )
                except Exception as e:
                    logger.warning(f"Could not send admin chat notification: {str(e)}")
            
            return (support_text, ConversationState.CHAT_SUPPORT_ACTIVE)

        # Handle FAQ command
        if intent == "faq":
            faq_text = ConversationService.get_faq_menu(db)
            return (faq_text, ConversationState.IDLE)

        # Handle specific FAQ categories
        if intent in ["faq_register", "faq_homework", "faq_payment", "faq_subscription"]:
            if "register" in intent:
                faq_text = (
                    "📝 Registration FAQs\n\n"
                    "Q: How do I create an account?\n"
                    "A: Tap 'Register' and follow the prompts. You'll need your name, email, and class/grade.\n\n"
                    "Q: Is registration free?\n"
                    "A: Yes! Creating an account is completely free.\n\n"
                    "Q: Can I change my details later?\n"
                    "A: Contact our support team for account changes."
                )
            elif "homework" in intent:
                faq_text = (
                    "📚 Homework FAQs\n\n"
                    "Q: Can I submit homework as text or image?\n"
                    "A: Yes! Choose text for typed answers or image for handwritten/picture submissions.\n\n"
                    "Q: How long does it take to get solutions?\n"
                    "A: A tutor will review and respond within 24 hours.\n\n"
                    "Q: Is there a limit to submissions?\n"
                    "A: Free users can submit with payment per homework. Subscribers have unlimited submissions."
                )
            elif "payment" in intent:
                faq_text = (
                    "💳 Payment FAQs\n\n"
                    "Q: What payment methods do you accept?\n"
                    "A: We accept Paystack payments (card, bank transfer, USSD).\n\n"
                    "Q: Is my payment information secure?\n"
                    "A: Yes! We use Paystack's secure payment gateway.\n\n"
                    "Q: Can I get a refund?\n"
                    "A: Refund requests are handled on a case-by-case basis."
                )
            elif "subscription" in intent:
                faq_text = (
                    "⭐ Subscription FAQs\n\n"
                    "Q: How much is the monthly subscription?\n"
                    "A: ₦5,000/month for unlimited homework submissions.\n\n"
                    "Q: Can I cancel my subscription?\n"
                    "A: Yes, you can cancel anytime without penalty.\n\n"
                    "Q: Do I get tutor support with subscription?\n"
                    "A: Yes! Subscribers get priority support from tutors."
                )
            return (faq_text, ConversationState.IDLE)

        # Initial state - user hasn't chosen action
        if current_state == ConversationState.INITIAL or current_state == ConversationState.IDLE:
            if intent == "register":
                # Check if user is already registered
                if student_data and student_data.get("name"):
                    # User is already registered - show their info with update menu
                    user_email = student_data.get("email", "Not provided")
                    user_class = student_data.get("class_grade", "Not provided")
                    return (
                        f"✅ You are already registered!\n\n"
                        f"📋 **Your Information:**\n\n"
                        f"👤 Name: {student_data.get('name')}\n"
                        f"📧 Email: {user_email}\n"
                        f"🎓 Class: {user_class}\n\n"
                        f"What would you like to do?",
                        ConversationState.ALREADY_REGISTERED,
                    )
                # Not registered - proceed with registration
                return (
                    "👤 Let's create your account!\n\n"
                    "What is your full name?",
                    ConversationState.REGISTERING_NAME,
                )
            elif intent == "update":
                # User wants to update their profile
                if not student_data or not student_data.get("name"):
                    return (
                        "❌ No Account Found\n\n"
                        "You don't have an account yet. Type 'Register' to create one.",
                        ConversationState.IDLE,
                    )
                # Start update profile process - begin with name
                current_name = student_data.get("name", "Not provided")
                return (
                    f"✏️ Update Your Profile\n\n"
                    f"Current Name: {current_name}\n\n"
                    f"Enter your new full name (or press skip to keep current name):",
                    ConversationState.UPDATING_NAME,
                )
            elif intent == "homework":
                if not student_data:
                    return (
                        "❌ Registration Required\n\n"
                        "You need to create an account first to submit homework. "
                        "Choose 'Register' to get started.",
                        ConversationState.IDLE,
                    )
                greeting = f"Hey {first_name}! 📝" if first_name else "📝"
                return (
                    f"{greeting}\n\nWhat subject is your homework for?\n\n"
                    "(e.g., Mathematics, English, Science)",
                    ConversationState.HOMEWORK_SUBJECT,
                )
            elif intent == "pay":
                if not student_data:
                    return (
                        "❌ Registration Required\n\n"
                        "You need to create an account first to subscribe. "
                        "Choose 'Register' to get started.",
                        ConversationState.IDLE,
                    )
                greeting = f"Hi {first_name}! 💳" if first_name else "💳"
                return (
                    f"{greeting}\n\n💰 Monthly Subscription\n"
                    f"Price: ₦5,000/month\n"
                    f"Unlimited homework submissions\n\n"
                    f"Tap 'Confirm Payment' to proceed.",
                    ConversationState.PAYMENT_PENDING,
                )
            elif intent == "check":
                if not student_data:
                    return (
                        "❌ Registration Required\n\n"
                        "You need to create an account first to check status. "
                        "Choose 'Register' to get started.",
                        ConversationState.IDLE,
                    )
                variables = {
                    "full_name": student_data.get("name", "User"),
                    "email": student_data.get("email", "Not provided"),
                    "has_subscription": "Yes" if student_data.get("has_subscription") else "No"
                }
                status_template = "status_subscribed" if student_data.get("has_subscription") else "status_not_subscribed"
                status_text = ConversationService.get_template(status_template, db, variables)
                if not status_text:
                    status = "✅ ACTIVE" if student_data.get("has_subscription") else "❌ INACTIVE"
                    greeting = f"{first_name}, y" if first_name else "Y"
                    status_text = (
                        f"📊 Subscription Status\n\n"
                        f"User: {greeting}our subscription\n"
                        f"Status: {status}"
                    )
                return (status_text, ConversationState.IDLE)
            elif intent == "main_menu":
                # If user clicks main menu from IDLE/INITIAL, return to main options
                menu_text = ConversationService.get_available_features_menu(db, first_name)
                return (
                    menu_text,
                    ConversationState.REGISTERED if student_data else ConversationState.IDLE,
                )
            else:
                greeting = f"👋 Hey {first_name}!" if first_name else "👋 Hi!"
                if first_name:
                    # Registered user - show feature list
                    menu_text = ConversationService.get_available_features_menu(db, first_name)
                    return (
                        menu_text,
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user
                    return (
                        f"{greeting}\n\nWelcome to Study Bot! Get started below.",
                        ConversationState.IDLE,
                    )

        # Already registered state - user tried to register but has account
        elif current_state == ConversationState.ALREADY_REGISTERED:
            if intent == "update":
                # User chose to update profile
                current_name = student_data.get("name", "Not provided")
                return (
                    f"✏️ Update Your Profile\n\n"
                    f"Current Name: {current_name}\n\n"
                    f"Enter your new full name (or type 'skip' to keep current name):",
                    ConversationState.UPDATING_NAME,
                )
            elif intent == "home" or intent == "main_menu":
                # User chose to return to main menu
                menu_text = ConversationService.get_available_features_menu(db, first_name)
                return (
                    menu_text,
                    ConversationState.IDLE,
                )
            else:
                # User sent unexpected input - show options again
                user_email = student_data.get("email", "Not provided") if student_data else "Not provided"
                user_class = student_data.get("class_grade", "Not provided") if student_data else "Not provided"
                return (
                    f"✅ You are already registered!\n\n"
                    f"📋 **Your Information:**\n\n"
                    f"👤 Name: {student_data.get('name') if student_data else 'N/A'}\n"
                    f"📧 Email: {user_email}\n"
                    f"🎓 Class: {user_class}\n\n"
                    f"What would you like to do?",
                    ConversationState.ALREADY_REGISTERED,
                )

        # Registration flow
        elif current_state == ConversationState.REGISTERING_NAME:
            ConversationService.set_data(phone_number, "full_name", message_text)
            return (
                "📧 Great!\n\nWhat is your email address?",
                ConversationState.REGISTERING_EMAIL,
            )

        elif current_state == ConversationState.REGISTERING_EMAIL:
            ConversationService.set_data(phone_number, "email", message_text)
            return (
                "🎓 Perfect!\n\nWhat is your class/grade?\n\n(e.g., 10A, SS2, Form 4)",
                ConversationState.REGISTERING_CLASS,
            )

        elif current_state == ConversationState.REGISTERING_CLASS:
            ConversationService.set_data(phone_number, "class_grade", message_text)
            full_name = ConversationService.get_data(phone_number, "full_name")
            first_name_reg = full_name.split()[0] if full_name else "there"
            
            # Show main menu after registration completion
            menu_text = f"✅ Account Created!\n\n{ConversationService.get_available_features_menu(db, first_name_reg)}"
            return (
                menu_text,
                ConversationState.REGISTERED,
            )

        # Profile update flow
        elif current_state == ConversationState.UPDATING_NAME:
            # Allow user to skip with "skip" command
            if "skip" in message_text.lower():
                # Keep existing name
                existing_name = student_data.get("name") if student_data else ""
                ConversationService.set_data(phone_number, "full_name", existing_name)
            else:
                ConversationService.set_data(phone_number, "full_name", message_text)
            
            current_email = student_data.get("email", "Not provided") if student_data else "Not provided"
            return (
                f"✅ Name updated!\n\n"
                f"Current Email: {current_email}\n\n"
                f"📧 Enter your new email address (or type 'skip' to keep current):",
                ConversationState.UPDATING_EMAIL,
            )

        elif current_state == ConversationState.UPDATING_EMAIL:
            # Allow user to skip
            if "skip" in message_text.lower():
                # Keep existing email
                existing_email = student_data.get("email") if student_data else ""
                ConversationService.set_data(phone_number, "email", existing_email)
            else:
                ConversationService.set_data(phone_number, "email", message_text)
            
            current_class = student_data.get("class_grade", "Not provided") if student_data else "Not provided"
            return (
                f"✅ Email updated!\n\n"
                f"Current Class: {current_class}\n\n"
                f"🎓 Enter your new class/grade (or type 'skip' to keep current):",
                ConversationState.UPDATING_CLASS,
            )

        elif current_state == ConversationState.UPDATING_CLASS:
            # Allow user to skip
            if "skip" in message_text.lower():
                # Keep existing class
                existing_class = student_data.get("class_grade") if student_data else ""
                ConversationService.set_data(phone_number, "class_grade", existing_class)
            else:
                ConversationService.set_data(phone_number, "class_grade", message_text)
            
            updated_name = ConversationService.get_data(phone_number, "full_name")
            updated_email = ConversationService.get_data(phone_number, "email")
            updated_class = ConversationService.get_data(phone_number, "class_grade")
            first_name_updated = updated_name.split()[0] if updated_name else "there"
            
            return (
                f"✅ Profile Updated!\n\n"
                f"📋 **Your Updated Information:**\n\n"
                f"👤 Name: {updated_name}\n"
                f"📧 Email: {updated_email}\n"
                f"🎓 Class: {updated_class}\n\n"
                f"What would you like to do next, {first_name_updated}?",
                ConversationState.IDLE,
            )

        # Chat support active - handle user messages during chat

        # Main menu - show welcome and main options (CHECK BEFORE REGISTERED STATE)
        elif intent == "main_menu":
            menu_text = ConversationService.get_available_features_menu(db, first_name)
            return (
                menu_text,
                ConversationState.REGISTERED,
            )

        # Registered user - handle intents
        elif current_state == ConversationState.REGISTERED:
            if intent == "homework":
                variables = {"first_name": first_name}
                homework_subject_text = ConversationService.get_template("homework_subject", db, variables)
                if not homework_subject_text:
                    greeting = f"Hey {first_name}! 📝" if first_name else "📝"
                    homework_subject_text = (
                        f"{greeting}\n\nWhat subject is your homework for?\n\n"
                        "(e.g., Mathematics, English, Science)"
                    )
                return (homework_subject_text, ConversationState.HOMEWORK_SUBJECT)
            elif intent == "pay":
                variables = {"first_name": first_name}
                payment_text = ConversationService.get_template("payment_info", db, variables)
                if not payment_text:
                    greeting = f"Hi {first_name}! 💳" if first_name else "💳"
                    payment_text = (
                        f"{greeting}\n\n💰 Monthly Subscription\n"
                        f"Price: ₦5,000/month\n"
                        f"Unlimited homework submissions\n\n"
                        f"Tap 'Confirm Payment' to proceed."
                    )
                return (payment_text, ConversationState.PAYMENT_PENDING)
            elif intent == "help":
                help_text = ConversationService.get_template("help_main", db)
                if not help_text:
                    help_text = (
                        f"📚 Help & Features\n\n"
                        f"🎓 EduBot helps you with:"
                        f"\n📝 Homework - Submit assignments and get tutor feedback"
                        f"\n💳 Subscribe - Unlock unlimited homework submissions (₦5,000/month)"
                        f"\n❓ FAQs - Quick answers to common questions"
                        f"\n💬 Chat Support - Talk to our support team"
                    )
                return (help_text, ConversationState.REGISTERED)
            else:
                # Default response for other intents while registered
                greeting = f"Hey {first_name}! 👋" if first_name else "👋"
                return (
                    f"{greeting}\n\nWhat would you like to do?",
                    ConversationState.REGISTERED,
                )

        # Homework flow
        elif current_state == ConversationState.HOMEWORK_SUBJECT:
            ConversationService.set_data(phone_number, "homework_subject", message_text)
            variables = {"subject": message_text}
            homework_type_text = ConversationService.get_template("homework_type", db, variables)
            if not homework_type_text:
                homework_type_text = f"📚 Subject: {message_text}\n\nHow would you like to submit your homework?"
            return (homework_type_text, ConversationState.HOMEWORK_TYPE)

        elif current_state == ConversationState.HOMEWORK_TYPE:
            submission_type = "IMAGE" if "image" in message_text.lower() else "TEXT"
            ConversationService.set_data(phone_number, "homework_type", submission_type)
            
            # For IMAGE, skip intermediate message and go directly to upload link
            if submission_type == "IMAGE":
                name_ref = f"{first_name}, " if first_name else ""
                return (
                    f"📷 {name_ref}preparing your upload page...",
                    ConversationState.HOMEWORK_SUBMITTED,
                )
            
            # For TEXT, ask for content
            else:
                name_ref = f"{first_name}, " if first_name else ""
                return (
                    f"📄 Text Submission\n\n"
                    f"{name_ref}Go ahead and send your homework now.",
                    ConversationState.HOMEWORK_CONTENT,
                )

        elif current_state == ConversationState.HOMEWORK_CONTENT:
            # Store the content (only TEXT submissions reach here)
            ConversationService.set_data(phone_number, "homework_content", message_text)
            name_ref = f"Thanks, {first_name}! " if first_name else ""
            return (
                f"{name_ref}📤 Processing your submission...\n\n"
                f"Your homework has been received and is being reviewed by a tutor.",
                ConversationState.HOMEWORK_SUBMITTED,
            )

        elif current_state == ConversationState.HOMEWORK_SUBMITTED:
            # Homework is now submitted - user can proceed
            # Show completion message and return to main menu
            name_ref = f"{first_name}, " if first_name else ""
            homework_subject = ConversationService.get_data(phone_number, "homework_subject")
            homework_type = ConversationService.get_data(phone_number, "homework_type")
            
            # Show confirmation based on submission type
            if homework_type == "IMAGE":
                confirmation = "Your image has been uploaded and submitted successfully! ✅"
            else:
                confirmation = "Your homework has been submitted successfully! ✅"
            
            return (
                f"{confirmation}\n\n"
                f"Subject: {homework_subject}\n"
                f"Type: {homework_type}\n\n"
                f"A tutor will review your work shortly.\n\n"
                f"What would you like to do next, {name_ref}?",
                ConversationState.IDLE,
            )

        # Payment flow
        elif current_state == ConversationState.PAYMENT_PENDING:
            if "confirm" in message_text.lower():
                name_ref = f"{first_name}, your" if first_name else "Your"
                return (
                    f"🔗 Payment Link\n\n"
                    f"{name_ref} payment link is ready. Click to complete payment on our secure gateway.\n\n"
                    f"We'll confirm once payment is received!",
                    ConversationState.PAYMENT_CONFIRMED,
                )
            else:
                return (
                    f"⚠️ Confirm Required\n\n"
                    f"Tap 'Confirm Payment' to proceed, or 'Cancel' to go back.",
                    ConversationState.PAYMENT_PENDING,
                )

        else:
            # Default response for unknown intent - show feature list
            if current_state in [ConversationState.INITIAL, ConversationState.IDLE, ConversationState.IDENTIFYING]:
                if student_data and student_data.get("name"):
                    # Registered user - show main menu
                    return (
                        ConversationService.get_available_features_menu(db, first_name),
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user - show main menu
                    return (
                        ConversationService.get_available_features_menu(db, ""),
                        ConversationState.INITIAL,
                    )
            else:
                # In other states, return to idle with feature list
                if student_data and student_data.get("name"):
                    return (
                        ConversationService.get_available_features_menu(db, first_name),
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user in other state - show main menu
                    return (
                        ConversationService.get_available_features_menu(db, ""),
                        ConversationState.INITIAL,
                    )
