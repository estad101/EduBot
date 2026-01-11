#!/usr/bin/env python
"""Update template with bold commands and emojis."""
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
        # Set template with bold commands and emojis
        template.template_content = "Hey {full_name}!\n\nAVAILABLE FEATURES:\n\n[Home] **Home** - Return to home menu\n[?] **FAQ** - Get answers to common questions\n[Book] **Homework** - Submit your homework\n[Chat] **Support** - Chat with our team\n[Card] **Subscribe** - View subscription plans\n[Info] **Status** - Check your account details\n[Help] **Help** - Get help with the bot\n\nJust type a command above to get started!"
        
        template.updated_at = datetime.utcnow()
        db.commit()
        print("✓ Template updated with bold commands and emojis")
    else:
        print("✗ Template not found")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
