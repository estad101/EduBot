#!/usr/bin/env python3
"""
Railway Environment Variables Setup Script
Securely adds environment variables to your Railway project via CLI

Usage:
1. Install Railway CLI: npm i -g @railway/cli
2. Login: railway login
3. Link project: railway link
4. Run this script: python setup_railway_env.py
"""

import os
import json
import subprocess
from pathlib import Path

# Your WhatsApp Credentials
WHATSAPP_CREDENTIALS = {
    "WHATSAPP_API_KEY": "EAAckpQFzzTUBQT73SGpogTNXAGImnudPIqyXef1CdhXZCZCfzxyS7KV6IcAQVaZBaQ8UiPjZA0ZAf7LZCHwX40n0fBBDMskmmrNwIRdE7xggPwXBNLltUq7FIoWnQjHPrEWUlkP8dBrYieWq2qmcMFPn57Ib0q8dDPN8HysJMNRJIC9ptQ8EJdUKYfeCTjmAZDZD",
    "WHATSAPP_PHONE_NUMBER_ID": "797467203457022",
    "WHATSAPP_BUSINESS_ACCOUNT_ID": "1516305056071819",
    "WHATSAPP_PHONE_NUMBER": "+15551610271",
}

# Standard Configuration Variables
STANDARD_ENV_VARS = {
    "API_TITLE": "EduBot API",
    "API_VERSION": "1.0.0",
    "API_PORT": "8000",
    "ENVIRONMENT": "production",
    "DEBUG": "False",
    "HTTPS_ONLY": "True",
    "ALGORITHM": "HS256",
    "SESSION_TIMEOUT_MINUTES": "60",
    "RATE_LIMIT_PER_MINUTE": "60",
    "MAX_FILE_SIZE_MB": "5",
    "ALLOWED_IMAGE_TYPES": "image/jpeg,image/png,image/webp",
    "UPLOADS_DIR": "uploads",
    "LOG_LEVEL": "WARNING",
    "NEXT_PUBLIC_APP_NAME": "EduBot",
}

# Variables that NEED YOUR INPUT
REQUIRES_INPUT = {
    "SECRET_KEY": "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'",
    "ADMIN_ORIGIN": "Your admin domain (e.g., https://admin.yourdomain.com)",
    "ALLOW_ORIGINS": "Your allowed domains (e.g., https://youradomain.com,https://api.yourdomain.com)",
    "NEXT_PUBLIC_API_URL": "Your API domain (e.g., https://api.yourdomain.com)",
    "PAYSTACK_PUBLIC_KEY": "From Paystack dashboard (pk_live_xxx)",
    "PAYSTACK_SECRET_KEY": "From Paystack dashboard (sk_live_xxx)",
    "PAYSTACK_WEBHOOK_SECRET": "Your webhook secret",
    "PAYSTACK_WEBHOOK_URL": "Your webhook URL",
    "WHATSAPP_WEBHOOK_TOKEN": "Your webhook token",
}


def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Railway CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("\n❌ Railway CLI not found!")
    print("Install it with: npm i -g @railway/cli")
    return False


def set_railway_variable(key: str, value: str) -> bool:
    """Set a single variable in Railway"""
    try:
        result = subprocess.run(
            ["railway", "variables", "set", key, value],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Set {key}")
            return True
        else:
            print(f"✗ Failed to set {key}: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error setting {key}: {e}")
        return False


def main():
    print("=" * 60)
    print("Railway Environment Variables Setup")
    print("=" * 60)
    
    # Check Railway CLI
    if not check_railway_cli():
        print("\nPlease install Railway CLI first:")
        print("  npm i -g @railway/cli")
        return
    
    # Check if linked to project
    print("\nChecking Railway project link...")
    result = subprocess.run(
        ["railway", "status"],
        capture_output=True,
        text=True
    )
    
    if "not linked" in result.stderr.lower() or result.returncode != 0:
        print("\n⚠️  Not linked to a Railway project!")
        print("Run: railway login")
        print("Then: railway link")
        return
    
    print("✓ Linked to Railway project")
    
    # Add WhatsApp credentials
    print("\n" + "=" * 60)
    print("Adding WhatsApp Credentials")
    print("=" * 60)
    
    success_count = 0
    for key, value in WHATSAPP_CREDENTIALS.items():
        if set_railway_variable(key, value):
            success_count += 1
    
    print(f"\n✓ Added {success_count}/{len(WHATSAPP_CREDENTIALS)} WhatsApp variables")
    
    # Add standard variables
    print("\n" + "=" * 60)
    print("Adding Standard Configuration Variables")
    print("=" * 60)
    
    success_count = 0
    for key, value in STANDARD_ENV_VARS.items():
        if set_railway_variable(key, value):
            success_count += 1
    
    print(f"\n✓ Added {success_count}/{len(STANDARD_ENV_VARS)} standard variables")
    
    # Request missing variables
    print("\n" + "=" * 60)
    print("⚠️  YOU MUST PROVIDE THESE VARIABLES")
    print("=" * 60)
    
    variables_to_add = {}
    
    for key, hint in REQUIRES_INPUT.items():
        print(f"\n{key}")
        print(f"  Hint: {hint}")
        value = input("  Enter value: ").strip()
        
        if value:
            variables_to_add[key] = value
        else:
            print(f"  ⚠️  Skipped! You can add this later in Railway dashboard")
    
    if variables_to_add:
        print("\n" + "=" * 60)
        print("Adding Your Custom Variables")
        print("=" * 60)
        
        success_count = 0
        for key, value in variables_to_add.items():
            if set_railway_variable(key, value):
                success_count += 1
        
        print(f"\n✓ Added {success_count}/{len(variables_to_add)} custom variables")
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Complete! 🎉")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check Railway dashboard to verify all variables")
    print("2. Run database migrations: railway run alembic upgrade head")
    print("3. Monitor deployment in Railway dashboard")
    print("4. Test your API once deployed")
    
    print("\nYour API will be available at:")
    print("  https://your-railway-project.railway.app")
    print("\nTest endpoint:")
    print("  curl https://your-railway-project.railway.app/api/health")


if __name__ == "__main__":
    main()
