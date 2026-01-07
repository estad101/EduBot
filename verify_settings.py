#!/usr/bin/env python3
"""
WhatsApp Settings Verification Script

This script verifies that the WhatsApp database settings system is working correctly.
Run this after deploying to production to verify everything initialized properly.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify all required modules can be imported."""
    print("\n📦 Verifying imports...")
    try:
        from config.database import SessionLocal
        print("  ✓ Database imported")
        
        from config.settings import settings
        print("  ✓ Settings imported")
        
        from models.settings import AdminSetting
        print("  ✓ AdminSetting model imported")
        
        from services.settings_service import (
            init_settings_from_db,
            get_setting,
            update_setting,
            refresh_cache,
            get_whatsapp_config
        )
        print("  ✓ SettingsService functions imported")
        
        from services.whatsapp_service import WhatsAppService
        print("  ✓ WhatsAppService imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def verify_database():
    """Verify database connection and admin_settings table."""
    print("\n💾 Verifying database...")
    try:
        from config.database import SessionLocal
        from models.settings import AdminSetting
        
        db = SessionLocal()
        
        # Check if table exists by querying
        result = db.query(AdminSetting).limit(1).all()
        print("  ✓ admin_settings table exists")
        
        # Count settings
        count = db.query(AdminSetting).count()
        print(f"  ✓ Found {count} settings in database")
        
        # Check for WhatsApp settings
        whatsapp_settings = db.query(AdminSetting).filter(
            AdminSetting.key.like('whatsapp%')
        ).all()
        print(f"  ✓ Found {len(whatsapp_settings)} WhatsApp settings")
        
        if whatsapp_settings:
            print("\n    WhatsApp Settings in Database:")
            for setting in whatsapp_settings:
                value_preview = f"{setting.value[:30]}..." if setting.value and len(setting.value) > 30 else (setting.value or "")
                print(f"      • {setting.key}: {value_preview if value_preview else '(empty)'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def verify_settings_service():
    """Verify SettingsService functionality."""
    print("\n⚙️  Verifying SettingsService...")
    try:
        from config.database import SessionLocal
        from services.settings_service import (
            init_settings_from_db,
            get_setting,
            get_whatsapp_config
        )
        
        db = SessionLocal()
        
        # Initialize settings
        init_settings_from_db(db)
        print("  ✓ Settings initialized from database")
        
        # Get a setting
        token = get_setting("whatsapp_api_key")
        if token:
            print(f"  ✓ Retrieved whatsapp_api_key ({len(token)} chars)")
        else:
            print("  ⚠ whatsapp_api_key not found (will fallback to env var)")
        
        # Get WhatsApp config
        config = get_whatsapp_config(db)
        print("  ✓ Retrieved complete WhatsApp config:")
        for key, value in config.items():
            if value:
                if len(str(value)) > 30:
                    print(f"      • {key}: {str(value)[:30]}...")
                else:
                    print(f"      • {key}: {value}")
            else:
                print(f"      • {key}: (not set)")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ✗ SettingsService error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_whatsapp_service():
    """Verify WhatsAppService can access credentials."""
    print("\n📱 Verifying WhatsAppService...")
    try:
        from services.whatsapp_service import WhatsAppService
        
        # Get credentials
        api_key, phone_number_id = WhatsAppService.get_api_credentials()
        
        if api_key:
            print(f"  ✓ Retrieved API key ({len(api_key)} chars)")
        else:
            print("  ✗ API key not found")
            return False
        
        if phone_number_id:
            print(f"  ✓ Retrieved phone number ID: {phone_number_id}")
        else:
            print("  ✗ Phone number ID not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ WhatsAppService error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_env_variables():
    """Verify environment variables as fallback."""
    print("\n🔐 Verifying environment variables...")
    
    from config.settings import settings
    
    env_vars = {
        'whatsapp_api_key': settings.whatsapp_api_key,
        'whatsapp_phone_number_id': settings.whatsapp_phone_number_id,
        'whatsapp_business_account_id': settings.whatsapp_business_account_id,
        'whatsapp_phone_number': settings.whatsapp_phone_number,
    }
    
    for key, value in env_vars.items():
        if value:
            if isinstance(value, str) and len(value) > 30:
                print(f"  ✓ {key}: {value[:30]}...")
            else:
                print(f"  ✓ {key}: {value}")
        else:
            print(f"  ⚠ {key}: not set in environment")
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("WhatsApp Database Settings Verification")
    print("=" * 60)
    
    checks = [
        ("Imports", verify_imports),
        ("Database", verify_database),
        ("SettingsService", verify_settings_service),
        ("WhatsAppService", verify_whatsapp_service),
        ("Environment Variables", verify_env_variables),
    ]
    
    results = {}
    for name, check in checks:
        try:
            results[name] = check()
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All checks passed! System is ready.")
        print("\nNext steps:")
        print("1. Go to https://your-app/settings")
        print("2. Verify WhatsApp credentials are displayed")
        print("3. Click 'Send Test Message'")
        print("4. Verify you receive the message on WhatsApp")
        return 0
    else:
        print("\n⚠️ Some checks failed. Review the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
