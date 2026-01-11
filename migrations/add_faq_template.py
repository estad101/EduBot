#!/usr/bin/env python
"""Add FAQ template to database."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime

db = SessionLocal()
try:
    # Check if FAQ template already exists
    existing = db.query(BotMessageTemplate).filter(
        BotMessageTemplate.template_name == "faq_main"
    ).first()
    
    if existing:
        print("✓ FAQ template 'faq_main' already exists, updating...")
        template = existing
    else:
        print("Creating new FAQ template...")
        template = BotMessageTemplate(template_name="faq_main")
    
    # Set the FAQ content
    template.template_content = """[?] Frequently Asked Questions

[Pen] Registration: Create account with name, email, class - it's FREE!

[Book] Homework: Submit text or images. Get tutor responses within 24 hours.

[Card] Payment: Subscribers enjoy unlimited homework submissions.

[Star] Subscription: Get premium access for continuous learning support."""
    
    template.variables = []
    template.is_default = True
    template.updated_at = datetime.utcnow()
    
    if not existing:
        db.add(template)
    
    db.commit()
    print("✓ FAQ template 'faq_main' saved successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
