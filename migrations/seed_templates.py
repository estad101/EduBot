"""
Seed bot_message_templates table with sample template data.
Run this script to populate the templates table.
"""
import logging
from config.database import SessionLocal
from models.bot_message import BotMessageTemplate

logger = logging.getLogger(__name__)


def seed_templates():
    """Seed default message templates."""
    try:
        db = SessionLocal()

        # Clear existing templates for development (optional - comment out for production)
        db.query(BotMessageTemplate).delete()
        db.commit()

        templates = [
            # Greeting Templates
            {
                "template_name": "greeting_welcome_new_user",
                "template_content": "👋 Welcome to {bot_name}!\n\nI'm {bot_name}, your friendly homework assistant. I'm here to help you submit assignments, get feedback, and improve your learning.\n\n🚀 Let's get started!",
                "variables": ["bot_name"],
                "is_default": True
            },
            {
                "template_name": "greeting_returning_user",
                "template_content": "Welcome back, {user_name}! 👋\n\nIt's great to see you again. What would you like to do today?",
                "variables": ["user_name"],
                "is_default": True
            },
            # Confirmation Templates
            {
                "template_name": "confirmation_action_success",
                "template_content": "✅ Success!\n\n{action} has been completed successfully.\n\nTimestamp: {timestamp}",
                "variables": ["action", "timestamp"],
                "is_default": True
            },
            {
                "template_name": "confirmation_registration",
                "template_content": "✅ Account Created Successfully!\n\nWelcome, {full_name}! 🎉\n\nYour account details:\n• Email: {email}\n• Class: {class}\n• Status: Active ✓\n\nYou can now submit homework, access FAQs, and use all features!",
                "variables": ["full_name", "email", "class"],
                "is_default": True
            },
            # Error Templates
            {
                "template_name": "error_invalid_input",
                "template_content": "❌ Invalid Input\n\nThe information you provided doesn't look right.\n\n{error_details}\n\nPlease try again.",
                "variables": ["error_details"],
                "is_default": True
            },
            {
                "template_name": "error_generic",
                "template_content": "❌ Oops! Something went wrong\n\nWe encountered an error processing your request.\n\nPlease try again or contact our support team for help.",
                "variables": [],
                "is_default": True
            },
            {
                "template_name": "error_unauthorized",
                "template_content": "🔒 Access Denied\n\nYou need to be registered to access this feature.\n\nWould you like to register now? Reply with 'register'",
                "variables": [],
                "is_default": True
            },
            # Prompt Templates
            {
                "template_name": "prompt_input_required",
                "template_content": "{prompt_text}\n\nPlease provide your response below:",
                "variables": ["prompt_text"],
                "is_default": True
            },
            {
                "template_name": "prompt_confirmation",
                "template_content": "{action_text}\n\nAre you sure? Reply with 'yes' to confirm or 'no' to cancel.",
                "variables": ["action_text"],
                "is_default": True
            },
            # Info Templates
            {
                "template_name": "info_subscription_status",
                "template_content": "📊 Your Subscription\n\n• Plan: {plan_name}\n• Status: {status}\n• Expires: {expiry_date}\n• Submissions Left: {submissions_left}/{limit}",
                "variables": ["plan_name", "status", "expiry_date", "submissions_left", "limit"],
                "is_default": True
            },
            {
                "template_name": "info_account_status",
                "template_content": "📋 Account Information\n\n👤 Name: {full_name}\n📧 Email: {email}\n🎓 Class: {class}\n📅 Joined: {join_date}\n⭐ Reputation: {reputation_score}\n📤 Submissions: {submission_count}",
                "variables": ["full_name", "email", "class", "join_date", "reputation_score", "submission_count"],
                "is_default": True
            },
            {
                "template_name": "info_pricing",
                "template_content": "💰 Subscription Plans\n\n🎯 Basic (Free)\n• {basic_limit} submissions/month\n• Standard support\n• Cost: Free\n\n⭐ Premium\n• Unlimited submissions\n• Priority support\n• {premium_price}/month\n\n👑 Pro\n• Everything in Premium\n• Direct tutor access\n• {pro_price}/month",
                "variables": ["basic_limit", "premium_price", "pro_price"],
                "is_default": True
            },
            # Menu Templates
            {
                "template_name": "menu_main_options",
                "template_content": "📚 What would you like to do?\n\nSelect an option below:",
                "variables": [],
                "is_default": True
            },
            {
                "template_name": "menu_yes_no",
                "template_content": "{question}\n\nReply 'yes' or 'no'",
                "variables": ["question"],
                "is_default": True
            },
            {
                "template_name": "menu_subject_selection",
                "template_content": "📚 Which subject?\n\nChoose from the options below:",
                "variables": [],
                "is_default": True
            },
            # Notification Templates
            {
                "template_name": "notification_submission_received",
                "template_content": "📬 Submission Received\n\nYour {subject} homework has been submitted:\n• Title: {title}\n• Time: {submission_time}\n• Status: Pending Review ⏳\n\nWe'll review and provide feedback soon!",
                "variables": ["subject", "title", "submission_time"],
                "is_default": True
            },
            {
                "template_name": "notification_feedback_ready",
                "template_content": "📝 Feedback Ready!\n\nYour {subject} submission has been reviewed:\n• Score: {score}/100\n• Feedback: {feedback_summary}\n\nTap to view detailed feedback.",
                "variables": ["subject", "score", "feedback_summary"],
                "is_default": True
            },
            {
                "template_name": "notification_payment_received",
                "template_content": "✅ Payment Confirmed\n\nThank you for subscribing!\n• Plan: {plan_name}\n• Amount: {amount}\n• Expires: {expiry_date}\n• Receipt ID: {receipt_id}",
                "variables": ["plan_name", "amount", "expiry_date", "receipt_id"],
                "is_default": True
            },
            # Help Templates
            {
                "template_name": "help_homework_submission",
                "template_content": "📝 How to Submit Homework\n\n1️⃣ Choose 'Homework' from the menu\n2️⃣ Select your subject\n3️⃣ Upload file or type your answer\n4️⃣ Submit and wait for feedback\n\nNeed more help? Type 'support'",
                "variables": [],
                "is_default": True
            },
            {
                "template_name": "help_payment_methods",
                "template_content": "💳 Payment Methods\n\nWe accept:\n✓ Debit Card\n✓ Credit Card\n✓ Bank Transfer\n✓ Mobile Money\n✓ Paystack\n\nAll payments are secure and encrypted.",
                "variables": [],
                "is_default": True
            },
            {
                "template_name": "help_frequently_asked",
                "template_content": "❓ Frequently Asked Questions\n\nPopular topics:\n1. How do I register?\n2. How do I submit homework?\n3. What's the pricing?\n4. How do I get feedback?\n5. Can I cancel my subscription?\n\nReply with the number to learn more.",
                "variables": [],
                "is_default": True
            },
        ]

        for tmpl in templates:
            try:
                template = BotMessageTemplate(
                    template_name=tmpl["template_name"],
                    template_content=tmpl["template_content"],
                    variables=tmpl.get("variables"),
                    is_default=tmpl.get("is_default", False)
                )
                db.add(template)
                logger.info(f"✓ Added template: {tmpl['template_name']}")
            except Exception as e:
                logger.error(f"Error adding template {tmpl['template_name']}: {str(e)}")

        db.commit()
        logger.info(f"\n✅ Successfully seeded {len(templates)} templates!")
        return True

    except Exception as e:
        logger.error(f"❌ Error seeding templates: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding bot_message_templates table...\n")
    if seed_templates():
        print("\n✅ Template seeding complete!")
    else:
        print("\n❌ Template seeding failed!")
