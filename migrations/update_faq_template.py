#!/usr/bin/env python
"""Update FAQ template with menu items."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime
import json

db = SessionLocal()
try:
    template = db.query(BotMessageTemplate).filter(
        BotMessageTemplate.template_name == "faq_main"
    ).first()
    
    if template:
        # Update template with better formatting and add menu items as JSON
        template.template_content = """[?] Frequently Asked Questions

[Pen] Registration: Create account with name, email, class - it's FREE!

[Book] Homework: Submit text or images. Get tutor responses within 24 hours.

[Card] Payment: Subscribers enjoy unlimited homework submissions.

[Star] Subscription: Get premium access for continuous learning support.

Reply with a number to learn more:
1. Registration
2. Homework
3. Payment
4. Subscription"""
        
        # Add menu items for buttons (JSON format)
        template.variables = ["faq_registration", "faq_homework", "faq_payment", "faq_subscription"]
        template.updated_at = datetime.utcnow()
        db.commit()
        print("✓ FAQ template updated with menu items")
    else:
        print("✗ FAQ template not found")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
