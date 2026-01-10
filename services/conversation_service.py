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

logger = logging.getLogger(__name__)

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
                {"id": "update", "title": "📝 Update"},
                {"id": "home", "title": "↩️ Home"},
            ]
        
        # Homework type selection - 2 options
        if current_state == ConversationState.HOMEWORK_TYPE:
            return [
                {"id": "text", "title": "📄 Text"},
                {"id": "image", "title": "📷 Image"},
            ]
        
        # Payment confirmation - 1 option  
        if current_state == ConversationState.PAYMENT_PENDING:
            return [
                {"id": "confirm", "title": "✅ Confirm Payment"},
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
                greeting = f"Hey {first_name}!" if first_name else "Hey there!"
                feature_text = (
                    f"{greeting}\n\n"
                    f"📚 **AVAILABLE FEATURES** 📚\n\n"
                    f"🏠 **Home** - Return to home menu\n"
                    f"❓ **FAQ** - Get answers to common questions\n"
                    f"📝 **Homework** - Submit your homework\n"
                    f"💬 **Support** - Chat with our team\n"
                    f"💳 **Subscribe** - View subscription plans\n"
                    f"📊 **Status** - Check your account details\n"
                    f"ℹ️ **Help** - Get help with the bot\n\n"
                    f"Just type a command above to get started!"
                )
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
                menu_text = (
                    f"{greeting}\n\n"
                    f"📚 **AVAILABLE FEATURES** 📚\n\n"
                    f"🏠 **Home** - Return to home menu\n"
                    f"❓ **FAQ** - Get answers to common questions\n"
                    f"📝 **Homework** - Submit your homework\n"
                    f"💬 **Support** - Chat with our team\n"
                    f"💳 **Subscribe** - View subscription plans\n"
                    f"📊 **Status** - Check your account details\n"
                    f"ℹ️ **Help** - Get help with the bot\n\n"
                    f"Just type a command above to get started!"
                )
                return (
                    menu_text,
                    ConversationState.IDLE,
                )
            else:
                # Generic cancel - just show menu
                greeting = f"Hey {first_name}!" if first_name else "Hey there!"
                menu_text = (
                    f"{greeting}\n\n"
                    f"📚 **AVAILABLE FEATURES** 📚\n\n"
                    f"🏠 **Home** - Return to home menu\n"
                    f"❓ **FAQ** - Get answers to common questions\n"
                    f"📝 **Homework** - Submit your homework\n"
                    f"💬 **Support** - Chat with our team\n"
                    f"💳 **Subscribe** - View subscription plans\n"
                    f"📊 **Status** - Check your account details\n"
                    f"ℹ️ **Help** - Get help with the bot\n\n"
                    f"Just type a command above to get started!"
                )
                return (
                    menu_text,
                    ConversationState.IDLE,
                )

        # Handle help command - Show comprehensive feature list
        if intent == "help":
            help_text = (
                f"📚 **STUDY BOT - COMPLETE FEATURES GUIDE** 📚\n\n"
                f"Our bot helps you succeed academically with these tools:\n\n"
                f"🎓 **KEY FEATURES:**\n\n"
                f"📝 **HOMEWORK SUBMISSIONS**\n"
                f"• Submit text-based answers or image uploads\n"
                f"• Get detailed feedback from expert tutors\n"
                f"• Response time: Within 24 hours\n\n"
                f"💳 **SUBSCRIPTION PLANS**\n"
                f"• FREE: Per-submission payment model\n"
                f"• PREMIUM: ₦5,000/month for unlimited submissions\n"
                f"• BONUS: Priority support for subscribers\n\n"
                f"❓ **KNOWLEDGE BASE (FAQs)**\n"
                f"• Registration guide: How to create your account\n"
                f"• Homework help: Submission tips and limits\n"
                f"• Payment info: Accepted methods and refund policy\n"
                f"• Subscription details: Plans and benefits\n\n"
                f"💬 **LIVE CHAT SUPPORT**\n"
                f"• Talk directly with our support team\n"
                f"• Available for all account types\n"
                f"• Quick responses to your questions\n\n"
                f"📊 **ACCOUNT MANAGEMENT**\n"
                f"• Check your subscription status anytime\n"
                f"• View your submission history\n"
                f"• Track tutor feedback\n\n"
                f"Ready to get started? Choose an option above!"
            )
            return (help_text, ConversationState.IDLE)

        # Handle chat support command
        if intent == "support":
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
            faq_text = (
                "❓ Frequently Asked Questions\n\n"
                "📝 Registration: Create account with name, email, class - it's FREE!\n\n"
                "📚 Homework: Submit text or images. Get tutor responses within 24 hours.\n\n"
                "💳 Payment: Subscribers enjoy unlimited homework submissions.\n\n"
                "⭐ Subscription: Get premium access for continuous learning support."
            )
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
                status = "✅ ACTIVE" if student_data.get("has_subscription") else "❌ INACTIVE"
                greeting = f"{first_name}, y" if first_name else "Y"
                return (
                    f"📊 Subscription Status\n\n"
                    f"User: {greeting}our subscription\n"
                    f"Status: {status}",
                    ConversationState.IDLE,
                )
            elif intent == "main_menu":
                # If user clicks main menu from IDLE/INITIAL, return to main options
                greeting = f"Welcome back, {first_name}! 👋" if first_name else "Welcome back! 👋"
                menu_text = (
                    f"{greeting}\n\n"
                    f"📚 **AVAILABLE FEATURES** 📚\n\n"
                    f"🏠 **Home** - Return to home menu\n"
                    f"❓ **FAQ** - Get answers to common questions\n"
                    f"📝 **Homework** - Submit your homework\n"
                    f"💬 **Support** - Chat with our team\n"
                    f"💳 **Subscribe** - View subscription plans\n"
                    f"📊 **Status** - Check your account details\n"
                    f"ℹ️ **Help** - Get help with the bot\n\n"
                    f"Just type a command above to get started!"
                )
                return (
                    menu_text,
                    ConversationState.REGISTERED if student_data else ConversationState.IDLE,
                )
            else:
                greeting = f"👋 Hey {first_name}!" if first_name else "👋 Hi!"
                if first_name:
                    # Registered user - show feature list
                    menu_text = (
                        f"{greeting}\n\n"
                        f"📚 **AVAILABLE FEATURES** 📚\n\n"
                        f"🏠 **Home** - Return to home menu\n"
                        f"❓ **FAQ** - Get answers to common questions\n"
                        f"📝 **Homework** - Submit your homework\n"
                        f"💬 **Support** - Chat with our team\n"
                        f"💳 **Subscribe** - View subscription plans\n"
                        f"📊 **Status** - Check your account details\n"
                        f"ℹ️ **Help** - Get help with the bot\n\n"
                        f"Just type a command above to get started!"
                    )
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
                greeting = f"Welcome back, {first_name}! 👋" if first_name else "Welcome back! 👋"
                return (
                    f"{greeting}\n\n"
                    f"📚 **AVAILABLE FEATURES** 📚\n\n"
                    f"🏠 **Home** - Return to home menu\n"
                    f"❓ **FAQ** - Get answers to common questions\n"
                    f"📝 **Homework** - Submit your homework\n"
                    f"💬 **Support** - Chat with our team\n"
                    f"💳 **Subscribe** - View subscription plans\n"
                    f"📊 **Status** - Check your account details\n"
                    f"ℹ️ **Help** - Get help with the bot\n\n"
                    f"Just type a command above to get started!",
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
            menu_text = (
                f"✅ Account Created!\n\n"
                f"Welcome, {first_name_reg}! 👋\n\n"
                f"📚 **AVAILABLE FEATURES** 📚\n\n"
                f"🏠 **Home** - Return to home menu\n"
                f"❓ **FAQ** - Get answers to common questions\n"
                f"📝 **Homework** - Submit your homework\n"
                f"💬 **Support** - Chat with our team\n"
                f"💳 **Subscribe** - View subscription plans\n"
                f"📊 **Status** - Check your account details\n"
                f"ℹ️ **Help** - Get help with the bot\n\n"
                f"Just type a command above to get started!"
            )
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
            greeting = f"Welcome back, {first_name}! 👋" if first_name else "Welcome back! 👋"
            menu_text = (
                f"{greeting}\n\n"
                f"📚 **AVAILABLE FEATURES** 📚\n\n"
                f"🏠 **Home** - Return to home menu\n"
                f"❓ **FAQ** - Get answers to common questions\n"
                f"📝 **Homework** - Submit your homework\n"
                f"💬 **Support** - Chat with our team\n"
                f"💳 **Subscribe** - View subscription plans\n"
                f"📊 **Status** - Check your account details\n"
                f"ℹ️ **Help** - Get help with the bot\n\n"
                f"Just type a command above to get started!"
            )
            return (
                menu_text,
                ConversationState.REGISTERED,
            )

        # Registered user - handle intents
        elif current_state == ConversationState.REGISTERED:
            if intent == "homework":
                greeting = f"Hey {first_name}! 📝" if first_name else "📝"
                return (
                    f"{greeting}\n\nWhat subject is your homework for?\n\n"
                    "(e.g., Mathematics, English, Science)",
                    ConversationState.HOMEWORK_SUBJECT,
                )
            elif intent == "pay":
                greeting = f"Hi {first_name}! 💳" if first_name else "💳"
                return (
                    f"{greeting}\n\n💰 Monthly Subscription\n"
                    f"Price: ₦5,000/month\n"
                    f"Unlimited homework submissions\n\n"
                    f"Tap 'Confirm Payment' to proceed.",
                    ConversationState.PAYMENT_PENDING,
                )
            elif intent == "help":
                return (
                    f"📚 Help & Features\n\n"
                    f"🎓 EduBot helps you with:"
                    f"\n📝 Homework - Submit assignments and get tutor feedback"
                    f"\n💳 Subscribe - Unlock unlimited homework submissions (₦5,000/month)"
                    f"\n❓ FAQs - Quick answers to common questions"
                    f"\n💬 Chat Support - Talk to our support team",
                    ConversationState.REGISTERED,
                )
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
            return (
                f"📚 Subject: {message_text}\n\n"
                f"How would you like to submit your homework?",
                ConversationState.HOMEWORK_TYPE,
            )

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
                    greeting = f"Hey {first_name}!" if first_name else "Hey there!"
                    return (
                        f"{greeting}\n\n"
                        f"📚 **AVAILABLE FEATURES** 📚\n\n"
                        f"🏠 **Home** - Return to home menu\n"
                        f"❓ **FAQ** - Get answers to common questions\n"
                        f"📝 **Homework** - Submit your homework\n"
                        f"💬 **Support** - Chat with our team\n"
                        f"💳 **Subscribe** - View subscription plans\n"
                        f"📊 **Status** - Check your account details\n"
                        f"ℹ️ **Help** - Get help with the bot\n\n"
                        f"Just type a command above to get started!",
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user - show main menu
                    return (
                        f"📚 **AVAILABLE FEATURES** 📚\n\n"
                        f"🏠 **Home** - Return to home menu\n"
                        f"❓ **FAQ** - Get answers to common questions\n"
                        f"📝 **Homework** - Submit your homework\n"
                        f"💬 **Support** - Chat with our support team\n"
                        f"💳 **Subscribe** - Check subscription plans & pricing\n"
                        f"📊 **Status** - View your account info\n"
                        f"ℹ️ **Help** - Learn how to use me\n\n"
                        f"To get started, type any command above or enter your full name to create an account!",
                        ConversationState.INITIAL,
                    )
            else:
                # In other states, return to idle with feature list
                if student_data and student_data.get("name"):
                    return (
                        f"📚 **AVAILABLE FEATURES** 📚\n\n"
                        f"🏠 **Home** - Return to home menu\n"
                        f"❓ **FAQ** - Get answers to common questions\n"
                        f"📝 **Homework** - Submit your homework\n"
                        f"💬 **Support** - Chat with our team\n"
                        f"💳 **Subscribe** - View subscription plans\n"
                        f"📊 **Status** - Check your account details\n"
                        f"ℹ️ **Help** - Get help with the bot\n\n"
                        f"Just type a command above to get started!",
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user in other state - show main menu
                    return (
                        f"📚 **AVAILABLE FEATURES** 📚\n\n"
                        f"🏠 **Home** - Return to home menu\n"
                        f"❓ **FAQ** - Get answers to common questions\n"
                        f"📝 **Homework** - Submit your homework\n"
                        f"💬 **Support** - Chat with our support team\n"
                        f"💳 **Subscribe** - Check subscription plans & pricing\n"
                        f"📊 **Status** - View your account info\n"
                        f"ℹ️ **Help** - Learn how to use me\n\n"
                        f"To get started, type any command above or enter your full name to create an account!",
                        ConversationState.INITIAL,
                    )
