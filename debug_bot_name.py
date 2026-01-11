#!/usr/bin/env python
"""Debug script to check database and API response."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.settings import AdminSetting
import json

db = SessionLocal()
try:
    print("=" * 60)
    print("DATABASE CHECK")
    print("=" * 60)
    
    # Check all settings
    all_settings = db.query(AdminSetting).all()
    print(f"\nTotal settings in database: {len(all_settings)}")
    
    # Find bot_name specifically
    bot_name_settings = [s for s in all_settings if s.key == 'bot_name']
    print(f"\nbot_name entries found: {len(bot_name_settings)}")
    
    for setting in bot_name_settings:
        print(f"  key: '{setting.key}'")
        print(f"  value: '{setting.value}'")
        print(f"  value type: {type(setting.value).__name__}")
        print(f"  value is None: {setting.value is None}")
        print(f"  value is empty string: {setting.value == ''}")
        print(f"  bool(value): {bool(setting.value)}")
    
    # Build a dict like the API does
    settings_dict = {}
    for setting in all_settings:
        settings_dict[setting.key] = setting.value or ""
    
    print(f"\nSettings dict bot_name: '{settings_dict.get('bot_name')}'")
    print(f"Settings dict bot_name is falsy: {not settings_dict.get('bot_name')}")
    
    print("\n" + "=" * 60)
    print("WHAT API WOULD RETURN")
    print("=" * 60)
    
    if not settings_dict.get("bot_name"):
        print("API would use default: 'EduBot'")
    else:
        print(f"API would return: '{settings_dict.get('bot_name')}'")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
