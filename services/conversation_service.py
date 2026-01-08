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
    KEYWORD_FAQ = ["faq", "faqs", "frequently asked", "question", "questions"]
    KEYWORD_SUPPORT = ["support", "chat", "help me", "agent", "human", "talk to someone"]
    KEYWORD_CANCEL = ["cancel", "stop", "reset", "clear", "menu"]

    @staticmethod
    def get_buttons(intent: str, current_state: ConversationState, is_registered: bool = False, phone_number: str = None) -> Optional[List[Dict[str, str]]]:
        """
        Get interactive buttons for a given state.

        Args:
            intent: Current user intent
            current_state: Current conversation state
            is_registered: Whether user is registered
            phone_number: User's phone number (for menu state lookup)

        Returns:
            List of button dicts with 'id' and 'title', or None for text-only responses
        """
        # STATE-BASED MENUS (CHECKED FIRST - Main menus always show regardless of intent)
        
        # Idle/Initial state buttons (Main Menu) - Toggle between FAQ menu and Homework menu
        if current_state in [ConversationState.INITIAL, ConversationState.IDLE, ConversationState.IDENTIFYING]:
            menu_state = ConversationService.get_data(phone_number, "menu_state") or "faq_menu" if phone_number else "faq_menu"
            
            if menu_state == "homework_menu":
                return [
                    {"id": "homework", "title": "📝 Homework"},
                    {"id": "pay", "title": "💳 Subscribe"},
                    {"id": "help", "title": "ℹ️ Help"},
                ]
            else:  # faq_menu (default)
                return [
                    {"id": "faq", "title": "❓ FAQs"},
                    {"id": "support", "title": "💬 Chat Support"},
                    {"id": "cancel", "title": "❌ Back"},
                ]

        # Registration complete - main menu
        if current_state == ConversationState.REGISTERED:
            return [
                {"id": "homework", "title": "📝 Homework"},
                {"id": "pay", "title": "💳 Subscribe"},
                {"id": "help", "title": "ℹ️ Help"},
            ]

        # Homework type selection
        if current_state == ConversationState.HOMEWORK_TYPE:
            return [
                {"id": "text", "title": "📄 Text"},
                {"id": "image", "title": "📷 Image"},
                {"id": "cancel", "title": "❌ Cancel"},
            ]

        # Payment confirmation
        if current_state == ConversationState.PAYMENT_PENDING:
            return [
                {"id": "confirm", "title": "✅ Confirm Payment"},
                {"id": "cancel", "title": "❌ Cancel"},
            ]

        # Homework submitted - what's next
        if current_state == ConversationState.HOMEWORK_SUBMITTED:
            return [
                {"id": "faq", "title": "❓ FAQs"},
                {"id": "support", "title": "💬 Chat Support"},
                {"id": "main_menu", "title": "📍 Main Menu"},
            ]

        # Registration flows - collect info with cancel option
        if current_state in [ConversationState.REGISTERING_NAME, ConversationState.REGISTERING_EMAIL, ConversationState.REGISTERING_CLASS]:
            return [
                {"id": "cancel", "title": "❌ Cancel"},
            ]

        # Homework input flows - collect info with cancel option
        if current_state in [ConversationState.HOMEWORK_SUBJECT, ConversationState.HOMEWORK_CONTENT]:
            return [
                {"id": "cancel", "title": "❌ Cancel"},
            ]

        # INTENT-BASED MENUS (CHECKED SECOND - Only when intent is explicit)
        
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

        # Check for keywords
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_REGISTER):
            return "register"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_HOMEWORK):
            return "homework"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_PAY):
            return "pay"
        if any(kw in text_lower for kw in MessageRouter.KEYWORD_CHECK):
            return "check"
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

        # Handle cancel command - Toggle menu state
        if intent == "cancel":
            # Toggle between faq_menu and homework_menu
            current_menu = ConversationService.get_data(phone_number, "menu_state") or "faq_menu"
            new_menu = "homework_menu" if current_menu == "faq_menu" else "faq_menu"
            ConversationService.set_data(phone_number, "menu_state", new_menu)
            
            greeting = f"Hey {first_name}!" if first_name else "Hey there!"
            return (
                f"{greeting}\n\nWhat would you like to do?",
                ConversationState.IDLE,
            )

        # Handle help command
        if intent == "help":
            return (
                f"📚 Help\n\n"
                f"Use the menu buttons to navigate:\n"
                f"• 📝 Homework - Submit your homework\n"
                f"• 💳 Subscribe - Manage your subscription\n"
                f"• ❌ Back - Switch between menus",
                ConversationState.IDLE,
            )

        # Handle chat support command
        if intent == "support":
            greeting = f"Hi {first_name}! 💬" if first_name else "💬"
            support_text = (
                f"{greeting}\n\n"
                f"📞 Live Chat Support\n\n"
                f"You can now chat with our support team. They're available Monday-Friday, 9AM-6PM WAT.\n\n"
                f"Please describe your issue and we'll help you as soon as possible!\n\n"
                f"(Note: Type your message naturally - a support agent will respond to you)"
            )
            return (support_text, ConversationState.IDLE)

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
                return (
                    "👤 Let's create your account!\n\n"
                    "What is your full name?",
                    ConversationState.REGISTERING_NAME,
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
            else:
                greeting = f"👋 Hey {first_name}!" if first_name else "👋 Hi!"
                if first_name:
                    # Registered user
                    return (
                        f"{greeting}\n\nWhat would you like to do?",
                        ConversationState.IDLE,
                    )
                else:
                    # Unregistered user
                    return (
                        f"{greeting}\n\nWelcome to Study Bot! Get started below.",
                        ConversationState.IDLE,
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
            return (
                f"✅ Account Created!\n\n"
                f"Welcome, {first_name_reg}!\n\n"
                f"You're now registered as a FREE user. You can submit homework "
                f"with payment per submission, or subscribe for unlimited access.\n\n"
                f"What would you like to do?",
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
                    f"📚 Help\n\n"
                    f"Use the menu buttons to navigate:\n"
                    f"• 📝 Homework - Submit your homework\n"
                    f"• 💳 Subscribe - Get premium access\n"
                    f"• ℹ️ Help - Get help (this menu)",
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
            icon = "📄" if submission_type == "TEXT" else "📷"
            name_ref = f"{first_name}, " if first_name else ""
            return (
                f"{icon} {submission_type} Submission\n\n"
                f"{name_ref}Go ahead and send your homework now.",
                ConversationState.HOMEWORK_CONTENT,
            )

        elif current_state == ConversationState.HOMEWORK_CONTENT:
            # Store the content - for text it's the message, for images it's stored as placeholder
            ConversationService.set_data(phone_number, "homework_content", message_text)
            name_ref = f"Thanks, {first_name}! " if first_name else ""
            return (
                f"{name_ref}📤 Processing your submission...\n\n"
                f"Your homework has been received and is being reviewed by a tutor.",
                ConversationState.HOMEWORK_SUBMITTED,
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
            # Default response for unknown intent on main menu
            if current_state in [ConversationState.INITIAL, ConversationState.IDLE, ConversationState.IDENTIFYING]:
                greeting = f"Hey {first_name}!" if first_name else "Hey there!"
                return (
                    f"{greeting}\n\nWhat would you like to do?",
                    ConversationState.IDLE,
                )
            else:
                return (
                    f"❓ I didn't quite understand that.\n\n"
                    f"Choose an option above to continue.",
                    ConversationState.IDLE,
                )
