#!/usr/bin/env python
"""Fix the corrupted template content."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime

db = SessionLocal()
try:
    template = db.query(BotMessageTemplate).filter(
        BotMessageTemplate.template_name == "available_features"
    ).first()
    
    if template:
        # Set clean template content - use plain text to avoid encoding issues
        template.template_content = "Hey {full_name}!\n\nAVAILABLE FEATURES:\n\nHome - Return to home menu\nFAQ - Get answers to common questions\nHomework - Submit your homework\nSupport - Chat with our team\nSubscribe - View subscription plans\nStatus - Check your account details\nHelp - Get help with the bot\n\nJust type a command above to get started!"
        
        template.updated_at = datetime.utcnow()
        db.commit()
        print("Template updated with plain text version")
    else:
        print("Template not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

