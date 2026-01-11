"""
Update script for the AVAILABLE FEATURES template.
Updates the template content to match the new format.
"""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime

def update():
    """Update AVAILABLE FEATURES template."""
    db = SessionLocal()
    try:
        # Find existing template
        template = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.template_name == "available_features"
        ).first()
        
        if not template:
            print("✗ Template 'available_features' not found")
            return
        
        # Update the template content
        template.template_content = """👋 Hey {full_name}!

🎁 **AVAILABLE FEATURES** 🎁

👤 **Home** - Return to home menu
❓ **FAQ** - Get answers to common questions
📚 **Homework** - Submit your homework
💬 **Support** - Chat with our team
💳 **Subscribe** - View subscription plans
📊 **Status** - Check your account details
ℹ️ **Help** - Get help with the bot

Just type a command above to get started!"""
        
        template.updated_at = datetime.utcnow()
        db.commit()
        print("✓ Template 'available_features' updated successfully")
        
    except Exception as e:
        print(f"✗ Error updating template: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update()
