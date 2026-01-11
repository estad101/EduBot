#!/usr/bin/env python
"""Verify and set bot_name in admin_settings if needed."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.settings import AdminSetting

db = SessionLocal()
try:
    # Delete any existing bot_name entries
    existing = db.query(AdminSetting).filter(AdminSetting.key == 'bot_name').all()
    for e in existing:
        db.delete(e)
        print(f"✓ Deleted old bot_name entry: {e.value}")
    
    db.commit()
    
    # Create fresh bot_name entry
    new_setting = AdminSetting(key='bot_name', value='SIL EduBot 101')
    db.add(new_setting)
    db.commit()
    print(f"✓ Created fresh bot_name: SIL EduBot 101")
    
    # Verify it was created
    verify = db.query(AdminSetting).filter(AdminSetting.key == 'bot_name').first()
    if verify:
        print(f"✓ Verified bot_name in database: {verify.value}")
    else:
        print("✗ Failed to verify bot_name")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
