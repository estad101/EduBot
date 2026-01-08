"""
Conversation State Management Service.

Tracks user conversation state across multiple message exchanges.
Manages registration, homework submission, and payment flows.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

# Conversation states
class ConversationState(str, Enum):
    """User conversation states."""

    INITIAL = "initial"  # New user
    IDENTIFYING = "identifying"  # Checking if existing user
    REGISTERING_NAME = "registering_name"
    REGISTERING_EMAIL = "registering_email"
    REGISTERING_CLASS = "registering_class"
    REGISTERED = "registered"
    HOMEWORK_SUBJECT = "homework_subject"
    HOMEWORK_TYPE = "homework_type"
    HOMEWORK_CONTENT = "homework_content"
    HOMEWORK_SUBMITTED = "homework_submitted"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CONFIRMED = "payment_confirmed"
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
    KEYWORD_CANCEL = ["cancel", "stop", "reset", "clear"]

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

        # Check for keywords
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_REGISTER):
            return "register"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_HOMEWORK):
            return "homework"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_PAY):
            return "pay"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_CHECK):
            return "check"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_HELP):
            return "help"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_CANCEL):
            return "cancel"

        return "unknown"

    @staticmethod
    def get_next_response(
        phone_number: str, message_text: str, student_data: Optional[Dict] = None
    ) -> tuple[str, Optional[ConversationState]]:
        """
        Get the next response based on conversation state and message.

        Args:
            phone_number: User's phone number
            message_text: User's message text
            student_data: Optional student data from database (includes name, status, etc.)

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

        # Handle cancel command
        if intent == "cancel":
            ConversationService.clear_state(phone_number)
            return (
                "❌ Conversation cleared. Type 'register', 'homework', 'pay', or 'help' to continue.",
                ConversationState.INITIAL,
            )

        # Handle help command
        if intent == "help":
            return (
                "📚 **Welcome to Study Bot!**\n\n"
                "Commands:\n"
                "• **register** - Create your student account\n"
                "• **homework** - Submit homework\n"
                "• **pay** - Buy a monthly subscription\n"
                "• **status** - Check your subscription\n"
                "• **cancel** - Reset conversation\n\n"
                "Type any command to get started!",
                ConversationState.IDLE,
            )

        # Initial state - user hasn't chosen action
        if current_state == ConversationState.INITIAL or current_state == ConversationState.IDLE:
            if intent == "register":
                return (
                    "✅ Let's register you! What is your full name?",
                    ConversationState.REGISTERING_NAME,
                )
            elif intent == "homework":
                if not student_data:
                    return (
                        "❌ You need to register first. Type 'register' to get started!",
                        ConversationState.IDLE,
                    )
                greeting = f"Hey {first_name}! 📝" if first_name else "📝"
                return (
                    f"{greeting} What subject is your homework for? (e.g., Mathematics, English, Science)",
                    ConversationState.HOMEWORK_SUBJECT,
                )
            elif intent == "pay":
                if not student_data:
                    return (
                        "❌ You need to register first. Type 'register' to get started!",
                        ConversationState.IDLE,
                    )
                greeting = f"Hi {first_name}! 💳" if first_name else "💳"
                return (
                    f"{greeting} Subscription: ₦5,000/month (unlimited homework submission)\n\n"
                    "Reply with 'confirm' to proceed with payment.",
                    ConversationState.PAYMENT_PENDING,
                )
            elif intent == "check":
                if not student_data:
                    return (
                        "❌ You need to register first. Type 'register' to get started!",
                        ConversationState.IDLE,
                    )
                status = "✅ Active" if student_data.get("has_subscription") else "❌ Inactive"
                greeting = f"{first_name}, y" if first_name else "Y"
                return (
                    f"📊 {greeting}our subscription status: {status}",
                    ConversationState.IDLE,
                )
            else:
                return (
                    "👋 Hi! Type 'help' for available commands, or:\n"
                    "• **register** - Create account\n"
                    "• **homework** - Submit homework\n"
                    "• **pay** - Get subscription\n"
                    "• **status** - Check subscription",
                    ConversationState.IDLE,
                )

        # Registration flow
        elif current_state == ConversationState.REGISTERING_NAME:
            ConversationService.set_data(phone_number, "full_name", message_text)
            return (
                "Great! What is your email address?",
                ConversationState.REGISTERING_EMAIL,
            )

        elif current_state == ConversationState.REGISTERING_EMAIL:
            ConversationService.set_data(phone_number, "email", message_text)
            return (
                "Perfect! What is your class/grade? (e.g., 10A, SS2, Form 4)",
                ConversationState.REGISTERING_CLASS,
            )

        elif current_state == ConversationState.REGISTERING_CLASS:
            ConversationService.set_data(phone_number, "class_grade", message_text)
            full_name = ConversationService.get_data(phone_number, "full_name")
            first_name_reg = full_name.split()[0] if full_name else "there"
            return (
                f"✅ Registration complete, {first_name_reg}! You are now registered as REGISTERED_FREE.\n\n"
                "You can now:\n"
                "• Submit homework (with payment per submission)\n"
                "• Buy monthly subscription for unlimited access\n\n"
                "Type 'homework' or 'pay' to continue!",
                ConversationState.REGISTERED,
            )

        # Homework flow
        elif current_state == ConversationState.HOMEWORK_SUBJECT:
            ConversationService.set_data(phone_number, "homework_subject", message_text)
            return (
                "Is this a **text** or **image** submission?",
                ConversationState.HOMEWORK_TYPE,
            )

        elif current_state == ConversationState.HOMEWORK_TYPE:
            submission_type = "IMAGE" if "image" in message_text.lower() else "TEXT"
            ConversationService.set_data(phone_number, "homework_type", submission_type)
            return (
                f"Got it, {submission_type} submission. Please send your homework now:",
                ConversationState.HOMEWORK_CONTENT,
            )

        elif current_state == ConversationState.HOMEWORK_CONTENT:
            ConversationService.set_data(phone_number, "homework_content", message_text)
            return (
                "📤 Processing your homework submission...",
                ConversationState.HOMEWORK_SUBMITTED,
            )

        # Payment flow
        elif current_state == ConversationState.PAYMENT_PENDING:
            if "confirm" in message_text.lower():
                return (
                    "🔗 Here's your payment link: [Payment Link]\n\n"
                    "Click to complete payment. We'll confirm once received!",
                    ConversationState.PAYMENT_CONFIRMED,
                )
            else:
                return (
                    "Type 'confirm' to proceed with payment, or 'cancel' to exit.",
                    ConversationState.PAYMENT_PENDING,
                )

        else:
            return (
                "Sorry, I didn't understand. Type 'help' for available commands.",
                ConversationState.IDLE,
            )
