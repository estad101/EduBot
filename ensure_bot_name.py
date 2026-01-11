#!/usr/bin/env python
"""Verify and set bot_name in admin_settings if needed."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.settings import AdminSetting

db = SessionLocal()
try:
    # Check existing bot_name
    bot_name = db.query(AdminSetting).filter(AdminSetting.key == 'bot_name').first()
    
    if bot_name:
        print(f"✓ Current bot_name: {bot_name.value}")
        # Update it to ensure it's properly set
        bot_name.value = "SIL EduBot 101"
        db.commit()
        print(f"✓ Updated bot_name to: {bot_name.value}")
    else:
        print("✗ bot_name not found in database - creating it")
        new_setting = AdminSetting(key='bot_name', value='SIL EduBot 101')
        db.add(new_setting)
        db.commit()
        print(f"✓ Created bot_name: SIL EduBot 101")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
