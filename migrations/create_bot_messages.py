"""
Migration script to create bot_messages tables.
Run this after updating models.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base, engine, SessionLocal
from models.bot_message import BotMessage, BotMessageTemplate, BotMessageWorkflow

logger = logging.getLogger(__name__)


def create_tables():
    """Create all bot message tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Bot message tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        return False


def seed_default_messages():
    """Seed default messages into the database."""
    try:
        db = SessionLocal()

        # Clear existing messages for development (optional - comment out for production)
        db.query(BotMessage).delete()
        db.commit()

        default_messages = [
            # Registration flow
            {
                "message_key": "registration_name_prompt",
                "message_type": "prompt",
                "context": "REGISTERING_NAME",
                "content": "What is your full name?",
                "has_menu": False,
                "next_states": ["REGISTERING_EMAIL"],
                "description": "Initial prompt for user's full name during registration"
            },
            {
                "message_key": "registration_email_prompt",
                "message_type": "prompt",
                "context": "REGISTERING_EMAIL",
                "content": "Great! What is your email address?",
                "has_menu": False,
                "next_states": ["REGISTERING_CLASS"],
                "description": "Prompt for user's email during registration"
            },
            {
                "message_key": "registration_class_prompt",
                "message_type": "prompt",
                "context": "REGISTERING_CLASS",
                "content": "Perfect! What is your class/grade?\n\n(e.g., 10A, SS2, Form 4)",
                "has_menu": False,
                "next_states": ["REGISTERED"],
                "description": "Prompt for user's class/grade during registration"
            },
            {
                "message_key": "registration_complete",
                "message_type": "confirmation",
                "context": "REGISTERED",
                "content": "✅ Account Created!\n\nWelcome, {full_name}! 👋\n\n📚 **AVAILABLE FEATURES** 📚\n\n🏠 **Home** - Return to home menu\n❓ **FAQ** - Get answers to common questions\n📝 **Homework** - Submit your homework\n💬 **Support** - Chat with our team\n💳 **Subscribe** - View subscription plans\n📊 **Status** - Check your account details\n\nJust type a command above to get started!",
                "has_menu": True,
                "menu_items": [
                    {"id": "home", "label": "🏠 Home", "action": "main_menu"},
                    {"id": "faq", "label": "❓ FAQ", "action": "faq"},
                    {"id": "homework", "label": "📝 Homework", "action": "homework"},
                    {"id": "support", "label": "💬 Support", "action": "support"},
                    {"id": "subscribe", "label": "💳 Subscribe", "action": "pay"},
                    {"id": "status", "label": "📊 Status", "action": "check"}
                ],
                "next_states": ["IDLE"],
                "variables": ["full_name"],
                "description": "Confirmation message shown after successful registration"
            },
            # Homework flow
            {
                "message_key": "homework_subject_prompt",
                "message_type": "prompt",
                "context": "HOMEWORK_SUBJECT",
                "content": "What subject is your homework for?\n\n(e.g., Mathematics, English, Science)",
                "has_menu": False,
                "next_states": ["HOMEWORK_TYPE"],
                "description": "Prompt for homework subject"
            },
            {
                "message_key": "homework_type_prompt",
                "message_type": "prompt",
                "context": "HOMEWORK_TYPE",
                "content": "How would you like to submit?",
                "has_menu": True,
                "menu_items": [
                    {"id": "text", "label": "📝 Text", "action": "text"},
                    {"id": "image", "label": "🖼️ Image", "action": "image"}
                ],
                "next_states": ["HOMEWORK_CONTENT"],
                "description": "Prompt for homework submission type (text or image)"
            },
            # Payment/Subscription flow
            {
                "message_key": "subscription_offer",
                "message_type": "info",
                "context": "PAYMENT_PENDING",
                "content": "💰 Monthly Subscription\nPrice: ₦5,000/month\nUnlimited homework submissions\n\nTap 'Confirm Payment' to proceed.",
                "has_menu": True,
                "menu_items": [
                    {"id": "confirm", "label": "✅ Confirm Payment", "action": "payment_confirm"},
                    {"id": "cancel", "label": "❌ Cancel", "action": "cancel"}
                ],
                "next_states": ["PAYMENT_CONFIRMED", "IDLE"],
                "description": "Subscription offer details with pricing"
            },
            # Main menu
            {
                "message_key": "main_menu",
                "message_type": "menu",
                "context": "IDLE",
                "content": "Welcome back! 👋\n\n📚 **AVAILABLE FEATURES** 📚\n\nJust type a command below to get started!",
                "has_menu": True,
                "menu_items": [
                    {"id": "home", "label": "🏠 Home", "action": "main_menu"},
                    {"id": "faq", "label": "❓ FAQ", "action": "faq"},
                    {"id": "homework", "label": "📝 Homework", "action": "homework"},
                    {"id": "support", "label": "💬 Support", "action": "support"},
                    {"id": "subscribe", "label": "💳 Subscribe", "action": "pay"},
                    {"id": "status", "label": "📊 Status", "action": "check"}
                ],
                "next_states": ["HOMEWORK_SUBJECT", "PAYMENT_PENDING", "CHAT_SUPPORT_ACTIVE"],
                "description": "Main menu displayed to registered users"
            },
            # Error messages
            {
                "message_key": "registration_required",
                "message_type": "error",
                "context": "IDLE",
                "content": "❌ Registration Required\n\nYou need to create an account first. Choose 'Register' to get started.",
                "has_menu": False,
                "description": "Error message when unregistered user tries to access features"
            },
            {
                "message_key": "error_generic",
                "message_type": "error",
                "context": "IDLE",
                "content": "❌ Error processing your message. Please try again.",
                "has_menu": False,
                "description": "Generic error message"
            },
            # FAQ section
            {
                "message_key": "faq_intro",
                "message_type": "info",
                "context": "FAQ_MENU",
                "content": "❓ **Frequently Asked Questions**\n\nChoose a topic below to learn more:",
                "has_menu": True,
                "menu_items": [
                    {"id": "how_register", "label": "📝 How do I register?", "action": "faq_registration"},
                    {"id": "how_submit", "label": "📤 How do I submit homework?", "action": "faq_homework"},
                    {"id": "pricing", "label": "💰 What's the pricing?", "action": "faq_pricing"},
                    {"id": "payment", "label": "💳 Payment methods?", "action": "faq_payment"},
                    {"id": "support", "label": "🆘 Need help?", "action": "support"}
                ],
                "next_states": ["IDLE"],
                "description": "FAQ menu with common questions"
            },
            {
                "message_key": "faq_registration",
                "message_type": "info",
                "context": "FAQ_REGISTRATION",
                "content": "📝 **How do I register?**\n\nRegistration is simple:\n1. Send 'Register' to start\n2. Provide your full name\n3. Enter your email address\n4. Tell us your class/grade\n5. Done! Your account is ready\n\nYou'll then have access to all features.",
                "has_menu": True,
                "menu_items": [
                    {"id": "back", "label": "⬅️ Back to FAQ", "action": "faq_menu"},
                    {"id": "home", "label": "🏠 Home", "action": "main_menu"}
                ],
                "next_states": ["FAQ_MENU", "IDLE"],
                "description": "FAQ answer about registration process"
            },
            # Support section
            {
                "message_key": "support_intro",
                "message_type": "info",
                "context": "CHAT_SUPPORT_ACTIVE",
                "content": "💬 **Chat Support**\n\nHello! Welcome to our support team. How can we help you today?\n\nYou can ask about:\n✅ Account issues\n✅ Homework submission\n✅ Payment problems\n✅ Technical issues\n✅ Other questions",
                "has_menu": True,
                "menu_items": [
                    {"id": "issue", "label": "📋 Report an issue", "action": "support_issue"},
                    {"id": "billing", "label": "💳 Billing question", "action": "support_billing"},
                    {"id": "other", "label": "❓ Other", "action": "support_other"},
                    {"id": "close", "label": "✅ Close chat", "action": "main_menu"}
                ],
                "next_states": ["IDLE"],
                "description": "Support chat introduction"
            },
            # Status/Account info
            {
                "message_key": "status_check",
                "message_type": "info",
                "context": "IDLE",
                "content": "📊 **Account Status**\n\nName: {full_name}\nEmail: {email}\nClass: {class}\nSubscription: {subscription_status}\nJoined: {join_date}",
                "has_menu": True,
                "menu_items": [
                    {"id": "back", "label": "⬅️ Back to menu", "action": "main_menu"}
                ],
                "next_states": ["IDLE"],
                "variables": ["full_name", "email", "class", "subscription_status", "join_date"],
                "description": "Display user account status and information"
            },
            # Welcome message
            {
                "message_key": "welcome_unregistered",
                "message_type": "greeting",
                "context": "IDLE",
                "content": "👋 Welcome to {bot_name}!\n\nI'm here to help you with homework submission and learning support.\n\n📌 **To get started:**\n\nType 'Register' to create an account, or ask me anything!",
                "has_menu": True,
                "menu_items": [
                    {"id": "register", "label": "📝 Register", "action": "register"},
                    {"id": "faq", "label": "❓ FAQ", "action": "faq_menu"},
                    {"id": "support", "label": "💬 Support", "action": "support_intro"}
                ],
                "next_states": ["REGISTERING_NAME", "FAQ_MENU", "CHAT_SUPPORT_ACTIVE"],
                "variables": ["bot_name"],
                "description": "Welcome message for unregistered users"
            },
            # Homework submission
            {
                "message_key": "homework_intro",
                "message_type": "info",
                "context": "HOMEWORK_SUBJECT",
                "content": "📝 **Homework Submission**\n\nLet's get started! Which subject is your homework for?\n\n🔹 Common subjects:\n• Mathematics\n• English\n• Science\n• History\n• Geography\n• Other",
                "has_menu": True,
                "menu_items": [
                    {"id": "math", "label": "📐 Mathematics", "action": "homework_math"},
                    {"id": "english", "label": "📚 English", "action": "homework_english"},
                    {"id": "science", "label": "🔬 Science", "action": "homework_science"},
                    {"id": "other", "label": "🔹 Other", "action": "homework_other"},
                    {"id": "cancel", "label": "❌ Cancel", "action": "main_menu"}
                ],
                "next_states": ["HOMEWORK_CONTENT"],
                "description": "Homework submission introduction with subject selection"
            },
            # Subscription info
            {
                "message_key": "subscription_plans",
                "message_type": "info",
                "context": "PAYMENT_PENDING",
                "content": "💳 **Subscription Plans**\n\n🎯 **Basic** - Free\n• Limited submissions (5/month)\n• Standard support\n\n⭐ **Premium** - ₦5,000/month\n• Unlimited submissions\n• Priority support\n• Detailed feedback\n\n👑 **Pro** - ₦10,000/month\n• Everything in Premium\n• Direct tutor access\n• Weekly progress reports",
                "has_menu": True,
                "menu_items": [
                    {"id": "basic", "label": "🎯 Basic (Free)", "action": "subscribe_basic"},
                    {"id": "premium", "label": "⭐ Premium", "action": "subscribe_premium"},
                    {"id": "pro", "label": "👑 Pro", "action": "subscribe_pro"},
                    {"id": "back", "label": "⬅️ Back", "action": "main_menu"}
                ],
                "next_states": ["PAYMENT_CONFIRMED", "IDLE"],
                "description": "Subscription plans overview"
            }

        ]

        for msg_data in default_messages:
            try:
                msg = BotMessage(
                    message_key=msg_data["message_key"],
                    message_type=msg_data["message_type"],
                    context=msg_data["context"],
                    content=msg_data["content"],
                    has_menu=msg_data.get("has_menu", False),
                    menu_items=msg_data.get("menu_items"),
                    next_states=msg_data.get("next_states"),
                    variables=msg_data.get("variables"),
                    description=msg_data.get("description"),
                    is_active=True,
                    created_by="system"
                )
                db.add(msg)
            except Exception as e:
                logger.error(f"Error creating message {msg_data['message_key']}: {str(e)}")

        db.commit()
        logger.info("✅ Default messages seeded successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error seeding messages: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating bot message tables...")
    create_tables()
    print("Seeding default messages...")
    seed_default_messages()
    print("✅ Migration complete!")
