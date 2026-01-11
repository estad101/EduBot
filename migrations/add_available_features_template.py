"""
Migration script to add the AVAILABLE FEATURES template to bot_message_templates.
This allows admins to customize the menu message through the settings page.
"""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime

def migrate():
    """Add AVAILABLE FEATURES template to database."""
    db = SessionLocal()
    try:
        # Check if template already exists
        existing = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.template_name == "available_features"
        ).first()
        
        if existing:
            print("✓ Template 'available_features' already exists")
            return
        
        # Create the template
        template = BotMessageTemplate(
            template_name="available_features",
            template_content="""📚 **AVAILABLE FEATURES** 📚

🏠 **Home** - Return to home menu
❓ **FAQ** - Get answers to common questions
📝 **Homework** - Submit your homework
💬 **Support** - Chat with our team
💳 **Subscribe** - View subscription plans
📊 **Status** - Check your account details

Just type a command above to get started!""",
            variables=["full_name", "bot_name"],
            is_default=True
        )
        
        db.add(template)
        db.commit()
        print("✓ Template 'available_features' created successfully")
        
    except Exception as e:
        print(f"✗ Error creating template: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
