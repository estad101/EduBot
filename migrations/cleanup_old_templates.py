#!/usr/bin/env python
"""Remove old/unwanted templates from the database."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate

# Keep only these templates - all others will be deleted
KEEP_TEMPLATES = {
    "available_features",
    "faq_main",
    "help_main",
    "support_welcome",
    "homework_subject",
    "homework_type",
    "payment_info",
    "subscription_details",
    "status_not_subscribed",
    "status_subscribed",
}

db = SessionLocal()
try:
    all_templates = db.query(BotMessageTemplate).all()
    
    deleted = 0
    kept = 0
    
    for template in all_templates:
        if template.template_name not in KEEP_TEMPLATES:
            db.delete(template)
            deleted += 1
            print(f"✓ Deleted: {template.template_name}")
        else:
            kept += 1
            print(f"✓ Kept: {template.template_name}")
    
    db.commit()
    print(f"\n✓ Cleanup complete: {deleted} deleted, {kept} kept")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
