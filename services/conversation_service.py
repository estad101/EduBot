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
    def extract_intent(message_text: str, button_id: Optional[str] = None) -> str:
        """
        Extract user intent from message text or button ID.

        Args:
            message_text: User's message text
            button_id: Button ID if message came from interactive button

        Returns:
            Intent string (register, homework, pay, check, help, cancel, unknown)
        """
        # First check button ID (takes precedence over text)
        if button_id:
            button_lower = button_id.lower()
            if "register" in button_lower:
                return "register"
            elif "homework" in button_lower:
                return "homework"
            elif "pay" in button_lower or "subscribe" in button_lower:
                return "pay"
            elif "status" in button_lower:
                return "check"
            elif "help" in button_lower:
                return "help"
            elif "cancel" in button_lower or "reset" in button_lower:
                return "cancel"
            elif "confirm" in button_lower:
                return "confirm"
            elif "text" in button_lower:
                return "text_submission"
            elif "image" in button_lower:
                return "image_submission"
        
        # Fall back to text-based intent detection
        text_lower = message_text.lower().strip() if message_text else ""

        # Check for more specific keywords first (before general ones)
        # Check "confirm" before other generic keywords
        if "confirm" in text_lower:
            return "confirm"
        
        # Check for keywords (specific order matters)
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
        
        # Check submission types
        if "text" in text_lower:
            return "text_submission"
        if "image" in text_lower:
            return "image_submission"

        return "unknown"

    @staticmethod
    def get_next_response(
        phone_number: str, message_text: str, student_data: Optional[Dict] = None, button_id: Optional[str] = None
    ) -> tuple[str, Optional[ConversationState]]:
        """
        Get the next response based on conversation state and message.

        Args:
            phone_number: User's phone number
            message_text: User's message text
            student_data: Optional student data from database
            button_id: Optional button ID if message came from interactive button

        Returns:
            Tuple of (response_message, next_state) or (response_message, next_state, button_data)
        """
        state = ConversationService.get_state(phone_number)
        current_state = state.get("state")
        intent = MessageRouter.extract_intent(message_text, button_id)

        # Handle cancel command (but not in payment flow - those are special)
        if intent == "cancel" and current_state != ConversationState.PAYMENT_PENDING:
            ConversationService.clear_state(phone_number)
            return (
                "❌ Conversation cleared. Type 'register', 'homework', 'pay', or 'help' to continue.",
                ConversationState.INITIAL,
            )

        # Handle help command
        if intent == "help":
            return (
                "👋 Hi! What would you like to do?",
                ConversationState.IDLE,
                {
                    "message_type": "interactive_buttons",
                    "buttons": [
                        {"id": "btn_register", "title": "📝 Register"},
                        {"id": "btn_homework", "title": "📚 Homework"},
                        {"id": "btn_pay", "title": "💳 Subscribe"},
                        {"id": "btn_status", "title": "✅ Status"},
                        {"id": "btn_cancel", "title": "❌ Reset"}
                    ]
                }
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
                return (
                    "📝 What subject is your homework for? (e.g., Mathematics, English, Science)",
                    ConversationState.HOMEWORK_SUBJECT,
                )
            elif intent == "pay":
                if not student_data:
                    return (
                        "❌ You need to register first. Type 'register' to get started!",
                        ConversationState.IDLE,
                    )
                return (
                    "💳 Subscription: ₦5,000/month (unlimited homework submission)\n\n"
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
                return (
                    f"📊 Your subscription status: {status}",
                    ConversationState.IDLE,
                )
            else:
                return (
                    "👋 Hi! What would you like to do?",
                    ConversationState.IDLE,
                    {
                        "message_type": "interactive_buttons",
                        "buttons": [
                            {"id": "btn_register", "title": "📝 Register"},
                            {"id": "btn_homework", "title": "📚 Homework"},
                            {"id": "btn_pay", "title": "💳 Subscribe"},
                            {"id": "btn_status", "title": "✅ Status"},
                            {"id": "btn_cancel", "title": "❌ Reset"}
                        ]
                    }
                )

        # Registration flow
        elif current_state == ConversationState.REGISTERING_NAME:
            ConversationService.set_data(phone_number, "full_name", message_text)
            return (
                "😊 Nice to meet you! What is your email address?",
                ConversationState.REGISTERING_EMAIL,
            )

        elif current_state == ConversationState.REGISTERING_EMAIL:
            ConversationService.set_data(phone_number, "email", message_text)
            return (
                "📚 Perfect! What is your class/grade?\n(e.g., 10A, SS2, Form 4)",
                ConversationState.REGISTERING_CLASS,
            )

        elif current_state == ConversationState.REGISTERING_CLASS:
            ConversationService.set_data(phone_number, "class_grade", message_text)
            return (
                "✅ Registration Complete!\n\nYou're now registered as a FREE student.\n\nSubmit homework or buy a monthly subscription for unlimited access.",
                ConversationState.REGISTERED,
                {
                    "message_type": "interactive_buttons",
                    "buttons": [
                        {"id": "btn_homework", "title": "📝 Submit Homework"},
                        {"id": "btn_pay", "title": "💳 Buy Subscription"}
                    ]
                }
            )

        # Homework flow
        elif current_state == ConversationState.HOMEWORK_SUBJECT:
            ConversationService.set_data(phone_number, "homework_subject", message_text)
            return (
                "📝 Is this a text or image submission?",
                ConversationState.HOMEWORK_TYPE,
                {
                    "message_type": "interactive_buttons",
                    "buttons": [
                        {"id": "btn_text", "title": "📝 Text"},
                        {"id": "btn_image", "title": "🖼️ Image"}
                    ]
                }
            )

        elif current_state == ConversationState.HOMEWORK_TYPE:
            # Determine submission type from button ID or message text
            if button_id and "image" in button_id.lower():
                submission_type = "IMAGE"
            elif button_id and "text" in button_id.lower():
                submission_type = "TEXT"
            else:
                submission_type = "IMAGE" if "image" in message_text.lower() else "TEXT"
            
            ConversationService.set_data(phone_number, "homework_type", submission_type)
            return (
                f"✍️ {submission_type} submission it is!\n\nPlease send your homework now:",
                ConversationState.HOMEWORK_CONTENT,
            )

        elif current_state == ConversationState.HOMEWORK_CONTENT:
            ConversationService.set_data(phone_number, "homework_content", message_text)
            return (
                "📤 Processing your homework submission...\n⏳ A tutor will review it shortly!",
                ConversationState.HOMEWORK_SUBMITTED,
            )

        # Payment flow
        elif current_state == ConversationState.PAYMENT_PENDING:
            # Check for confirmation from button or text
            if (button_id and "confirm" in button_id.lower()) or ("confirm" in message_text.lower() and intent == "confirm"):
                return (
                    "💳 Opening payment page...\n\nComplete payment and we'll send you a confirmation!\n\nAfter payment you'll unlock unlimited homework submissions and get expert tutor feedback.",
                    ConversationState.PAYMENT_CONFIRMED,
                )
            elif (button_id and "cancel" in button_id.lower()) or ("cancel" in message_text.lower() and intent == "cancel"):
                return (
                    "❌ Payment cancelled. You can try again anytime by typing 'pay'.",
                    ConversationState.IDLE,
                )
            else:
                return (
                    "💳 Subscription: ₦5,000/month\n\nUnlimited homework submissions and expert feedback included.",
                    ConversationState.PAYMENT_PENDING,
                    {
                        "message_type": "interactive_buttons",
                        "buttons": [
                            {"id": "btn_confirm", "title": "✅ Confirm Payment"},
                            {"id": "btn_cancel", "title": "❌ Cancel"}
                        ]
                    }
                )

        else:
            return (
                "Sorry, I didn't understand that. 🤔\n\nType 'help' for available commands.",
                ConversationState.IDLE,
            )
