#!/usr/bin/env python3
"""
WhatsApp Delivery Diagnostic Tool.
Checks if WhatsApp credentials and webhook are properly configured.
"""
import os
import sys
from config.settings import settings

def check_environment():
    """Check if all required WhatsApp environment variables are set."""
    print("\n" + "="*60)
    print("WhatsApp Configuration Diagnostic")
    print("="*60)
    
    # Check WhatsApp API Key
    if settings.whatsapp_api_key == "placeholder_api_key":
        print("❌ WHATSAPP_API_KEY: NOT SET (using placeholder)")
        return False
    else:
        print(f"✅ WHATSAPP_API_KEY: SET ({settings.whatsapp_api_key[:20]}...)")
    
    # Check WhatsApp Phone Number ID
    if settings.whatsapp_phone_number_id == "placeholder_phone_id":
        print("❌ WHATSAPP_PHONE_NUMBER_ID: NOT SET (using placeholder)")
        return False
    else:
        print(f"✅ WHATSAPP_PHONE_NUMBER_ID: SET ({settings.whatsapp_phone_number_id})")
    
    # Check Webhook Token
    if not settings.whatsapp_webhook_token:
        print("⚠️  WHATSAPP_WEBHOOK_TOKEN: NOT SET (required for webhook verification)")
        return False
    else:
        print(f"✅ WHATSAPP_WEBHOOK_TOKEN: SET")
    
    # Check Phone Number
    if not settings.whatsapp_phone_number:
        print("⚠️  WHATSAPP_PHONE_NUMBER: NOT SET (for reference only)")
    else:
        print(f"✅ WHATSAPP_PHONE_NUMBER: SET ({settings.whatsapp_phone_number})")
    
    print("\n" + "-"*60)
    print("Summary:")
    print("-"*60)
    print("""
REQUIRED for WhatsApp delivery to work:
1. WHATSAPP_API_KEY - Bearer token from Meta/Facebook
2. WHATSAPP_PHONE_NUMBER_ID - Your WhatsApp Business Account phone number ID
3. WHATSAPP_WEBHOOK_TOKEN - Custom token for webhook verification

OPTIONAL but recommended:
4. WHATSAPP_PHONE_NUMBER - Your WhatsApp number (for reference)
5. WHATSAPP_BUSINESS_ACCOUNT_ID - Your Business Account ID
    """)
    print("\nTo set these in Railway:")
    print("1. Go to your Railway project dashboard")
    print("2. Select Variables")
    print("3. Add the environment variables above")
    print("4. Redeploy the application")
    
    return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
